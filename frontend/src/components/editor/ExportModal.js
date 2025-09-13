import React, { useState } from 'react';
import { X, Download, Crown, AlertCircle } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

const ExportModal = ({ isOpen, onClose, onExport, loading }) => {
  const [selectedFormat, setSelectedFormat] = useState('MP4');
  const [selectedResolution, setSelectedResolution] = useState('1080p');
  
  const { user } = useAuth();

  const formats = [
    {
      id: 'MP4',
      name: 'MP4 Video',
      description: 'Universal video format',
      icon: '🎬',
      resolutions: ['720p', '1080p', '4K']
    },
    {
      id: 'GIF',
      name: 'Animated GIF',
      description: 'Perfect for social media',
      icon: '🎞️',
      resolutions: ['480p', '720p']
    },
    {
      id: 'JSON',
      name: 'Lottie JSON',
      description: 'Vector animation for web',
      icon: '📄',
      resolutions: ['Vector']
    }
  ];

  const getMaxResolution = (tier) => {
    switch (tier) {
      case 'free': return '720p';
      case 'mid': return '1080p';
      case 'pro': return '4K';
      default: return '720p';
    }
  };

  const canUseResolution = (resolution) => {
    if (!user) return false;
    
    const maxRes = getMaxResolution(user.subscription_tier);
    const resolutionOrder = ['480p', '720p', '1080p', '4K'];
    const maxIndex = resolutionOrder.indexOf(maxRes);
    const currentIndex = resolutionOrder.indexOf(resolution);
    
    return currentIndex <= maxIndex;
  };

  const handleExport = () => {
    onExport(selectedFormat, selectedResolution);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-lg w-full p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-semibold text-gray-900">Export Animation</h3>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Format Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Export Format
          </label>
          <div className="grid grid-cols-1 gap-3">
            {formats.map((format) => (
              <button
                key={format.id}
                onClick={() => {
                  setSelectedFormat(format.id);
                  setSelectedResolution(format.resolutions[0]);
                }}
                className={`p-4 border-2 rounded-lg text-left transition-colors ${
                  selectedFormat === format.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center">
                  <span className="text-2xl mr-3">{format.icon}</span>
                  <div>
                    <div className="font-medium text-gray-900">{format.name}</div>
                    <div className="text-sm text-gray-600">{format.description}</div>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Resolution Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Resolution
          </label>
          <div className="grid grid-cols-2 gap-2">
            {formats.find(f => f.id === selectedFormat)?.resolutions.map((resolution) => {
              const canUse = canUseResolution(resolution);
              
              return (
                <button
                  key={resolution}
                  onClick={() => setSelectedResolution(resolution)}
                  disabled={!canUse}
                  className={`p-3 border rounded-lg transition-colors ${
                    selectedResolution === resolution
                      ? 'border-blue-500 bg-blue-50'
                      : canUse
                      ? 'border-gray-200 hover:border-gray-300'
                      : 'border-gray-200 bg-gray-50 opacity-50 cursor-not-allowed'
                  }`}
                >
                  <div className="font-medium">{resolution}</div>
                  {!canUse && (
                    <div className="text-xs text-orange-600 flex items-center mt-1">
                      <Crown className="w-3 h-3 mr-1" />
                      Upgrade required
                    </div>
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* User Credits Info */}
        {user && (
          <div className="mb-6 bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-gray-900">Credits Available</div>
                <div className="text-sm text-gray-600">
                  {user.credits_remaining} exports remaining this month
                </div>
              </div>
              <div className="flex items-center">
                <Crown className="w-5 h-5 text-orange-500 mr-2" />
                <span className="text-sm font-medium text-gray-900 capitalize">
                  {user.subscription_tier} Plan
                </span>
              </div>
            </div>
            
            {user.credits_remaining <= 0 && (
              <div className="mt-3 p-3 bg-orange-50 border border-orange-200 rounded-lg">
                <div className="flex items-center">
                  <AlertCircle className="w-4 h-4 text-orange-600 mr-2" />
                  <p className="text-orange-600 text-sm">
                    No credits remaining. Upgrade your plan to continue exporting.
                  </p>
                </div>
              </div>
            )}
            
            {user.subscription_tier === 'free' && (
              <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center">
                  <AlertCircle className="w-4 h-4 text-blue-600 mr-2" />
                  <p className="text-blue-600 text-sm">
                    Free plan exports include a watermark. Upgrade to remove it.
                  </p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Export Button */}
        <button
          onClick={handleExport}
          disabled={loading || !user || user.credits_remaining <= 0}
          className="w-full py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold rounded-lg hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent mr-2"></div>
              Exporting...
            </>
          ) : (
            <>
              <Download className="w-5 h-5 mr-2" />
              Export {selectedFormat} ({selectedResolution})
            </>
          )}
        </button>

        {!user && (
          <div className="mt-4 p-4 bg-orange-50 border border-orange-200 rounded-lg">
            <p className="text-orange-600 text-sm text-center">
              Please sign in to export your animations
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ExportModal;