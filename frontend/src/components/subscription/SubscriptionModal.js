import React, { useState, useEffect } from 'react';
import { X, Check, Crown, Zap, Star } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { apiService } from '../../services/api';
import PaymentModal from './PaymentModal';

const SubscriptionModal = ({ isOpen, onClose }) => {
  const [plans, setPlans] = useState({});
  const [currentSubscription, setCurrentSubscription] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [showPayment, setShowPayment] = useState(false);
  const [billingCycle, setBillingCycle] = useState('monthly');
  
  const { user } = useAuth();

  useEffect(() => {
    if (isOpen) {
      loadSubscriptionData();
    }
  }, [isOpen]);

  const loadSubscriptionData = async () => {
    try {
      const [plansData, subscriptionData] = await Promise.all([
        apiService.getSubscriptionPlans(),
        apiService.getCurrentSubscription()
      ]);
      
      setPlans(plansData);
      setCurrentSubscription(subscriptionData);
    } catch (error) {
      console.error('Failed to load subscription data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPlan = (planKey) => {
    if (planKey === 'free') return; // Can't "buy" free plan
    
    setSelectedPlan(planKey);
    setShowPayment(true);
  };

  const getPlanIcon = (tier) => {
    switch (tier) {
      case 'free':
        return <Star className="w-6 h-6" />;
      case 'mid':
        return <Zap className="w-6 h-6" />;
      case 'pro':
        return <Crown className="w-6 h-6" />;
      default:
        return <Star className="w-6 h-6" />;
    }
  };

  const getPlanColor = (tier) => {
    switch (tier) {
      case 'free':
        return 'text-gray-600';
      case 'mid':
        return 'text-blue-600';
      case 'pro':
        return 'text-purple-600';
      default:
        return 'text-gray-600';
    }
  };

  const getPlanGradient = (tier) => {
    switch (tier) {
      case 'free':
        return 'from-gray-500 to-gray-600';
      case 'mid':
        return 'from-blue-500 to-blue-600';
      case 'pro':
        return 'from-purple-500 to-purple-600';
      default:
        return 'from-gray-500 to-gray-600';
    }
  };

  const isCurrentPlan = (tier) => {
    return user?.subscription_tier === tier;
  };

  if (!isOpen) return null;

  if (showPayment && selectedPlan) {
    return (
      <PaymentModal
        isOpen={true}
        onClose={() => {
          setShowPayment(false);
          setSelectedPlan(null);
        }}
        plan={plans[selectedPlan]}
        billingCycle={billingCycle}
        onSuccess={() => {
          setShowPayment(false);
          setSelectedPlan(null);
          onClose();
          loadSubscriptionData();
        }}
      />
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-4xl w-full p-8 relative max-h-[90vh] overflow-y-auto">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Choose Your Plan</h2>
          <p className="text-gray-600">Unlock the full potential of MotionEdit</p>
        </div>

        {/* Billing Toggle */}
        <div className="flex justify-center mb-8">
          <div className="bg-gray-100 rounded-lg p-1 flex">
            <button
              onClick={() => setBillingCycle('monthly')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                billingCycle === 'monthly'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingCycle('yearly')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                billingCycle === 'yearly'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Yearly
              <span className="ml-1 text-xs bg-green-100 text-green-600 px-2 py-1 rounded-full">
                Save 17%
              </span>
            </button>
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {Object.entries(plans).map(([planKey, plan]) => (
              <div
                key={planKey}
                className={`relative bg-white border-2 rounded-2xl p-6 ${
                  planKey === 'mid' 
                    ? 'border-blue-500 shadow-lg scale-105' 
                    : 'border-gray-200 hover:border-gray-300'
                } transition-all duration-200`}
              >
                {planKey === 'mid' && (
                  <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                    <span className="bg-blue-500 text-white px-4 py-1 rounded-full text-sm font-medium">
                      Most Popular
                    </span>
                  </div>
                )}

                <div className="text-center">
                  <div className={`inline-flex items-center justify-center w-12 h-12 rounded-full bg-gradient-to-r ${getPlanGradient(planKey)} text-white mb-4`}>
                    {getPlanIcon(planKey)}
                  </div>
                  
                  <h3 className="text-xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                  
                  <div className="mb-6">
                    <span className="text-3xl font-bold text-gray-900">
                      ${billingCycle === 'monthly' ? plan.price_monthly : plan.price_yearly}
                    </span>
                    <span className="text-gray-600">
                      /{billingCycle === 'monthly' ? 'month' : 'year'}
                    </span>
                  </div>

                  <ul className="space-y-3 mb-8 text-left">
                    {plan.features.map((feature, index) => (
                      <li key={index} className="flex items-start">
                        <Check className="w-5 h-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                        <span className="text-gray-700">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  {isCurrentPlan(planKey) ? (
                    <button
                      disabled
                      className="w-full py-3 bg-gray-100 text-gray-500 font-semibold rounded-lg cursor-not-allowed"
                    >
                      Current Plan
                    </button>
                  ) : planKey === 'free' ? (
                    <button
                      disabled
                      className="w-full py-3 border border-gray-300 text-gray-500 font-semibold rounded-lg cursor-not-allowed"
                    >
                      Free Plan
                    </button>
                  ) : (
                    <button
                      onClick={() => handleSelectPlan(planKey)}
                      className={`w-full py-3 bg-gradient-to-r ${getPlanGradient(planKey)} text-white font-semibold rounded-lg hover:shadow-lg transition-all duration-200`}
                    >
                      {user?.subscription_tier === 'free' ? 'Get Started' : 'Upgrade'}
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Current Usage */}
        {user && (
          <div className="mt-8 bg-gray-50 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Current Usage</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">{user.credits_remaining}</div>
                <div className="text-sm text-gray-600">Credits Remaining</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900 capitalize">{user.subscription_tier}</div>
                <div className="text-sm text-gray-600">Current Plan</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {plans[user.subscription_tier]?.max_resolution || 'N/A'}
                </div>
                <div className="text-sm text-gray-600">Max Resolution</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SubscriptionModal;