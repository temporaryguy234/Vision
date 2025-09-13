import React from 'react';
import { Crown, Zap, X } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

const SubscriptionBanner = ({ onUpgrade, onDismiss }) => {
  const { user } = useAuth();

  if (!user || user.subscription_tier !== 'free' || user.credits_remaining > 1) {
    return null;
  }

  return (
    <div className="bg-gradient-to-r from-orange-500 to-red-500 text-white p-4 relative">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center">
          <Crown className="w-6 h-6 mr-3" />
          <div>
            <h3 className="font-semibold">Running low on credits!</h3>
            <p className="text-sm opacity-90">
              You have {user.credits_remaining} export{user.credits_remaining !== 1 ? 's' : ''} remaining. 
              Upgrade to get more credits and unlock premium features.
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <button
            onClick={onUpgrade}
            className="bg-white text-orange-600 px-4 py-2 rounded-lg font-medium hover:bg-gray-100 transition-colors flex items-center"
          >
            <Zap className="w-4 h-4 mr-2" />
            Upgrade Now
          </button>
          
          {onDismiss && (
            <button
              onClick={onDismiss}
              className="p-2 text-white hover:bg-white/20 rounded-lg transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default SubscriptionBanner;