import React, { useState, useEffect } from 'react';
import { X, CreditCard, Shield } from 'lucide-react';
import { loadStripe } from '@stripe/stripe-js';
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js';
import { apiService } from '../../services/api';

const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY);

const PaymentForm = ({ plan, billingCycle, onSuccess, onError }) => {
  const stripe = useStripe();
  const elements = useElements();
  const [loading, setLoading] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState('stripe');

  const handleStripePayment = async (e) => {
    e.preventDefault();
    
    if (!stripe || !elements) return;
    
    setLoading(true);
    
    try {
      const amount = billingCycle === 'monthly' ? plan.price_monthly : plan.price_yearly;
      
      // Create payment intent
      const { client_secret } = await apiService.createPaymentIntent({
        amount,
        currency: 'usd',
        subscription_tier: plan.tier,
        payment_method: 'stripe'
      });

      // Confirm payment
      const { error, paymentIntent } = await stripe.confirmCardPayment(client_secret, {
        payment_method: {
          card: elements.getElement(CardElement),
        }
      });

      if (error) {
        onError(error.message);
      } else if (paymentIntent.status === 'succeeded') {
        onSuccess();
      }
    } catch (error) {
      onError(error.message || 'Payment failed');
    } finally {
      setLoading(false);
    }
  };

  const handlePayPalPayment = async () => {
    setLoading(true);
    
    try {
      const amount = billingCycle === 'monthly' ? plan.price_monthly : plan.price_yearly;
      
      const result = await apiService.createPaymentIntent({
        amount,
        currency: 'usd',
        subscription_tier: plan.tier,
        payment_method: 'paypal'
      });

      if (result.approval_url) {
        window.location.href = result.approval_url;
      } else {
        onError('Failed to create PayPal payment');
      }
    } catch (error) {
      onError(error.message || 'PayPal payment failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Payment Method Selection */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Payment Method</h3>
        <div className="grid grid-cols-2 gap-4">
          <button
            onClick={() => setPaymentMethod('stripe')}
            className={`p-4 border-2 rounded-lg flex items-center justify-center transition-colors ${
              paymentMethod === 'stripe'
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <CreditCard className="w-5 h-5 mr-2" />
            Credit Card
          </button>
          
          <button
            onClick={() => setPaymentMethod('paypal')}
            className={`p-4 border-2 rounded-lg flex items-center justify-center transition-colors ${
              paymentMethod === 'paypal'
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
              <path fill="#0070ba" d="M7.076 21.337H2.47a.641.641 0 0 1-.633-.74L4.944.901C5.026.382 5.474 0 5.998 0h7.46c2.57 0 4.578.543 5.69 1.81 1.01 1.15 1.304 2.42 1.012 4.287-.023.143-.047.288-.077.437-.983 5.05-4.349 6.797-8.647 6.797h-2.19c-.524 0-.968.382-1.05.9l-1.12 7.106zm14.146-14.42a3.35 3.35 0 0 0-.607-.541c-.013.076-.026.175-.041.254-.93 4.778-4.005 7.201-9.138 7.201h-2.19a.9.9 0 0 0-.885.75l-1.274 8.067a.641.641 0 0 0 .633.74h4.608a.641.641 0 0 0 .633-.74l.034-.214.65-4.119.042-.267a.641.641 0 0 1 .633-.74h.4c3.131 0 5.583-1.275 6.299-4.96.299-1.54.144-2.823-.477-3.431z"/>
            </svg>
            PayPal
          </button>
        </div>
      </div>

      {paymentMethod === 'stripe' ? (
        <form onSubmit={handleStripePayment}>
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Card Information
            </label>
            <div className="border border-gray-300 rounded-lg p-4">
              <CardElement
                options={{
                  style: {
                    base: {
                      fontSize: '16px',
                      color: '#424770',
                      '::placeholder': {
                        color: '#aab7c4',
                      },
                    },
                  },
                }}
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={!stripe || loading}
            className="w-full py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold rounded-lg hover:shadow-lg transition-all duration-200 disabled:opacity-50"
          >
            {loading ? 'Processing...' : `Pay $${billingCycle === 'monthly' ? plan.price_monthly : plan.price_yearly}`}
          </button>
        </form>
      ) : (
        <div className="text-center">
          <button
            onClick={handlePayPalPayment}
            disabled={loading}
            className="w-full py-3 bg-gradient-to-r from-yellow-500 to-yellow-600 text-white font-semibold rounded-lg hover:shadow-lg transition-all duration-200 disabled:opacity-50"
          >
            {loading ? 'Redirecting...' : `Pay with PayPal - $${billingCycle === 'monthly' ? plan.price_monthly : plan.price_yearly}`}
          </button>
        </div>
      )}

      <div className="flex items-center justify-center text-sm text-gray-500">
        <Shield className="w-4 h-4 mr-2" />
        Secure payment powered by Stripe & PayPal
      </div>
    </div>
  );
};

const PaymentModal = ({ isOpen, onClose, plan, billingCycle, onSuccess }) => {
  const [error, setError] = useState('');

  const handleSuccess = () => {
    setError('');
    onSuccess();
  };

  const handleError = (errorMessage) => {
    setError(errorMessage);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-md w-full p-8 relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Complete Payment</h2>
          <p className="text-gray-600">
            Upgrading to {plan.name} - ${billingCycle === 'monthly' ? plan.price_monthly : plan.price_yearly}/{billingCycle === 'monthly' ? 'month' : 'year'}
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-600 text-sm">{error}</p>
          </div>
        )}

        <Elements stripe={stripePromise}>
          <PaymentForm
            plan={plan}
            billingCycle={billingCycle}
            onSuccess={handleSuccess}
            onError={handleError}
          />
        </Elements>
      </div>
    </div>
  );
};

export default PaymentModal;