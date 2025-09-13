import os
import stripe
import paypalrestsdk
from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from pydantic import BaseModel
from datetime import datetime
import uuid

# Stripe Configuration
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')

# PayPal Configuration
paypalrestsdk.configure({
    "mode": os.environ.get('PAYPAL_MODE', 'sandbox'),  # sandbox or live
    "client_id": os.environ.get('PAYPAL_CLIENT_ID'),
    "client_secret": os.environ.get('PAYPAL_CLIENT_SECRET')
})

class PaymentIntent(BaseModel):
    amount: float
    currency: str = "usd"
    subscription_tier: str
    payment_method: str  # stripe or paypal

class PaymentResult(BaseModel):
    success: bool
    payment_id: str
    client_secret: Optional[str] = None  # For Stripe
    approval_url: Optional[str] = None   # For PayPal
    error: Optional[str] = None

class PaymentService:
    def __init__(self, db):
        self.db = db
    
    async def create_stripe_payment_intent(
        self, 
        user_id: str, 
        amount: float, 
        subscription_tier: str
    ) -> PaymentResult:
        """Create Stripe payment intent"""
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency='usd',
                metadata={
                    'user_id': user_id,
                    'subscription_tier': subscription_tier,
                    'type': 'subscription'
                }
            )
            
            # Store payment record
            payment_doc = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "stripe_payment_intent_id": intent.id,
                "amount": amount,
                "currency": "usd",
                "subscription_tier": subscription_tier,
                "status": "pending",
                "payment_method": "stripe",
                "created_at": datetime.utcnow()
            }
            
            await self.db.payments.insert_one(payment_doc)
            
            return PaymentResult(
                success=True,
                payment_id=intent.id,
                client_secret=intent.client_secret
            )
            
        except stripe.error.StripeError as e:
            return PaymentResult(
                success=False,
                payment_id="",
                error=str(e)
            )
    
    async def create_paypal_payment(
        self, 
        user_id: str, 
        amount: float, 
        subscription_tier: str
    ) -> PaymentResult:
        """Create PayPal payment"""
        try:
            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "redirect_urls": {
                    "return_url": f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/payment/success",
                    "cancel_url": f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/payment/cancel"
                },
                "transactions": [{
                    "item_list": {
                        "items": [{
                            "name": f"MotionEdit {subscription_tier.title()} Subscription",
                            "sku": f"subscription_{subscription_tier}",
                            "price": str(amount),
                            "currency": "USD",
                            "quantity": 1
                        }]
                    },
                    "amount": {
                        "total": str(amount),
                        "currency": "USD"
                    },
                    "description": f"MotionEdit {subscription_tier.title()} subscription"
                }]
            })
            
            if payment.create():
                # Store payment record
                payment_doc = {
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "paypal_payment_id": payment.id,
                    "amount": amount,
                    "currency": "USD",
                    "subscription_tier": subscription_tier,
                    "status": "pending",
                    "payment_method": "paypal",
                    "created_at": datetime.utcnow()
                }
                
                await self.db.payments.insert_one(payment_doc)
                
                # Get approval URL
                approval_url = None
                for link in payment.links:
                    if link.rel == "approval_url":
                        approval_url = link.href
                        break
                
                return PaymentResult(
                    success=True,
                    payment_id=payment.id,
                    approval_url=approval_url
                )
            else:
                return PaymentResult(
                    success=False,
                    payment_id="",
                    error=str(payment.error)
                )
                
        except Exception as e:
            return PaymentResult(
                success=False,
                payment_id="",
                error=str(e)
            )
    
    async def confirm_stripe_payment(self, payment_intent_id: str) -> bool:
        """Confirm Stripe payment and activate subscription"""
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if intent.status == 'succeeded':
                # Update payment record
                await self.db.payments.update_one(
                    {"stripe_payment_intent_id": payment_intent_id},
                    {
                        "$set": {
                            "status": "completed",
                            "completed_at": datetime.utcnow()
                        }
                    }
                )
                
                # Activate subscription
                user_id = intent.metadata.get('user_id')
                subscription_tier = intent.metadata.get('subscription_tier')
                
                if user_id and subscription_tier:
                    from subscription import SubscriptionService
                    subscription_service = SubscriptionService(self.db)
                    await subscription_service.create_subscription(
                        user_id, 
                        SubscriptionTier(subscription_tier)
                    )
                
                return True
            
            return False
            
        except stripe.error.StripeError:
            return False
    
    async def confirm_paypal_payment(self, payment_id: str, payer_id: str) -> bool:
        """Confirm PayPal payment and activate subscription"""
        try:
            payment = paypalrestsdk.Payment.find(payment_id)
            
            if payment.execute({"payer_id": payer_id}):
                # Update payment record
                payment_doc = await self.db.payments.find_one({"paypal_payment_id": payment_id})
                
                if payment_doc:
                    await self.db.payments.update_one(
                        {"paypal_payment_id": payment_id},
                        {
                            "$set": {
                                "status": "completed",
                                "completed_at": datetime.utcnow()
                            }
                        }
                    )
                    
                    # Activate subscription
                    user_id = payment_doc['user_id']
                    subscription_tier = payment_doc['subscription_tier']
                    
                    from subscription import SubscriptionService
                    subscription_service = SubscriptionService(self.db)
                    await subscription_service.create_subscription(
                        user_id, 
                        SubscriptionTier(subscription_tier)
                    )
                    
                    return True
            
            return False
            
        except Exception:
            return False
    
    async def handle_stripe_webhook(self, payload: bytes, sig_header: str) -> bool:
        """Handle Stripe webhook events"""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
            
            if event['type'] == 'payment_intent.succeeded':
                payment_intent = event['data']['object']
                await self.confirm_stripe_payment(payment_intent['id'])
            
            elif event['type'] == 'invoice.payment_succeeded':
                # Handle subscription renewal
                invoice = event['data']['object']
                customer_id = invoice['customer']
                
                # Find user by Stripe customer ID and refresh credits
                user_doc = await self.db.users.find_one({"stripe_customer_id": customer_id})
                if user_doc:
                    from subscription import SubscriptionService
                    subscription_service = SubscriptionService(self.db)
                    await subscription_service.refresh_monthly_credits(user_doc['id'])
            
            return True
            
        except Exception as e:
            print(f"Stripe webhook error: {e}")
            return False
    
    def get_subscription_plans(self) -> Dict[str, SubscriptionPlan]:
        """Get all available subscription plans"""
        return {tier.value: plan for tier, plan in self.plans.items()}