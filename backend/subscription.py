from enum import Enum
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pydantic import BaseModel
from fastapi import HTTPException, status
import uuid

class SubscriptionTier(str, Enum):
    FREE = "free"
    MID = "mid"
    PRO = "pro"

class SubscriptionPlan(BaseModel):
    tier: SubscriptionTier
    name: str
    price_monthly: float
    price_yearly: float
    credits_per_month: int
    max_resolution: str
    has_watermark: bool
    features: list[str]

class Subscription(BaseModel):
    id: str
    user_id: str
    tier: SubscriptionTier
    status: str  # active, cancelled, expired
    current_period_start: datetime
    current_period_end: datetime
    credits_remaining: int
    auto_renew: bool = True
    payment_method: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class SubscriptionService:
    def __init__(self, db):
        self.db = db
        self.plans = {
            SubscriptionTier.FREE: SubscriptionPlan(
                tier=SubscriptionTier.FREE,
                name="Free",
                price_monthly=0.0,
                price_yearly=0.0,
                credits_per_month=5,
                max_resolution="720p",
                has_watermark=True,
                features=[
                    "5 exports per month",
                    "720p maximum resolution",
                    "Watermark on exports",
                    "Basic templates access"
                ]
            ),
            SubscriptionTier.MID: SubscriptionPlan(
                tier=SubscriptionTier.MID,
                name="Creator",
                price_monthly=19.99,
                price_yearly=199.99,
                credits_per_month=50,
                max_resolution="1080p",
                has_watermark=False,
                features=[
                    "50 exports per month",
                    "1080p maximum resolution",
                    "No watermark",
                    "Premium templates access",
                    "Priority support"
                ]
            ),
            SubscriptionTier.PRO: SubscriptionPlan(
                tier=SubscriptionTier.PRO,
                name="Professional",
                price_monthly=39.99,
                price_yearly=399.99,
                credits_per_month=100,
                max_resolution="4K",
                has_watermark=False,
                features=[
                    "100 exports per month",
                    "4K maximum resolution",
                    "No watermark",
                    "All templates access",
                    "Advanced AI features",
                    "Priority support",
                    "Commercial license"
                ]
            )
        }
    
    async def get_user_subscription(self, user_id: str) -> Optional[Subscription]:
        """Get user's current subscription"""
        subscription_doc = await self.db.subscriptions.find_one({
            "user_id": user_id,
            "status": "active"
        })
        
        if subscription_doc:
            return Subscription(**subscription_doc)
        return None
    
    async def create_subscription(
        self, 
        user_id: str, 
        tier: SubscriptionTier,
        payment_method: str = "stripe"
    ) -> Subscription:
        """Create a new subscription"""
        # Cancel existing subscription if any
        await self.cancel_subscription(user_id)
        
        # Create new subscription
        now = datetime.utcnow()
        subscription_doc = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "tier": tier,
            "status": "active",
            "current_period_start": now,
            "current_period_end": now + timedelta(days=30),
            "credits_remaining": self.plans[tier].credits_per_month,
            "auto_renew": True,
            "payment_method": payment_method,
            "created_at": now,
            "updated_at": now
        }
        
        await self.db.subscriptions.insert_one(subscription_doc)
        
        # Update user's subscription tier
        await self.db.users.update_one(
            {"id": user_id},
            {
                "$set": {
                    "subscription_tier": tier,
                    "credits_remaining": self.plans[tier].credits_per_month,
                    "subscription_expires": subscription_doc["current_period_end"]
                }
            }
        )
        
        return Subscription(**subscription_doc)
    
    async def cancel_subscription(self, user_id: str) -> bool:
        """Cancel user's subscription"""
        result = await self.db.subscriptions.update_many(
            {"user_id": user_id, "status": "active"},
            {
                "$set": {
                    "status": "cancelled",
                    "auto_renew": False,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0
    
    async def use_credit(self, user_id: str) -> bool:
        """Use one credit for export"""
        user_doc = await self.db.users.find_one({"id": user_id})
        if not user_doc:
            return False
        
        credits = user_doc.get('credits_remaining', 0)
        if credits <= 0:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="No credits remaining. Please upgrade your subscription."
            )
        
        # Deduct credit
        await self.db.users.update_one(
            {"id": user_id},
            {"$inc": {"credits_remaining": -1}}
        )
        
        return True
    
    async def refresh_monthly_credits(self, user_id: str) -> bool:
        """Refresh monthly credits (called by cron job)"""
        subscription = await self.get_user_subscription(user_id)
        if not subscription:
            return False
        
        # Check if it's time to refresh
        if datetime.utcnow() >= subscription.current_period_end:
            plan = self.plans[subscription.tier]
            
            # Update subscription period and credits
            new_period_end = subscription.current_period_end + timedelta(days=30)
            
            await self.db.subscriptions.update_one(
                {"id": subscription.id},
                {
                    "$set": {
                        "current_period_start": subscription.current_period_end,
                        "current_period_end": new_period_end,
                        "credits_remaining": plan.credits_per_month,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            await self.db.users.update_one(
                {"id": user_id},
                {
                    "$set": {
                        "credits_remaining": plan.credits_per_month,
                        "subscription_expires": new_period_end
                    }
                }
            )
            
            return True
        
        return False
    
    def get_plan(self, tier: SubscriptionTier) -> SubscriptionPlan:
        """Get subscription plan details"""
        return self.plans[tier]
    
    def get_all_plans(self) -> Dict[str, SubscriptionPlan]:
        """Get all available plans"""
        return self.plans
    
    async def check_export_permissions(self, user: User, resolution: str) -> bool:
        """Check if user can export at given resolution"""
        plan = self.plans[SubscriptionTier(user.subscription_tier)]
        
        resolution_hierarchy = {
            "480p": 1,
            "720p": 2,
            "1080p": 3,
            "4K": 4
        }
        
        max_res_level = resolution_hierarchy.get(plan.max_resolution, 1)
        requested_res_level = resolution_hierarchy.get(resolution, 4)
        
        return requested_res_level <= max_res_level
    
    def should_add_watermark(self, user: User) -> bool:
        """Check if exports should have watermark"""
        plan = self.plans[SubscriptionTier(user.subscription_tier)]
        return plan.has_watermark