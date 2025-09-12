import React, { useState, useEffect } from 'react';
import { Download, Calendar, FileVideo, Image, File, Eye, Trash2, RefreshCw } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { apiService } from '../services/api';

const ExportsPage = () => {
  const [activeTab, setActiveTab] = useState('history');
  const [exports, setExports] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const { user } = useAuth();

  useEffect(() => {
    loadExports();
  }, []);

  const loadExports = async () => {
    try {
      const exportsData = await apiService.getUserExports();
      setExports(exportsData);
    } catch (error) {
      console.error('Failed to load exports:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteExport = async (exportId) => {
    if (!confirm('Are you sure you want to delete this export?')) return;
    
    try {
      await apiService.deleteExport(exportId);
      setExports(exports.filter(exp => exp.id !== exportId));
    } catch (error) {
      alert('Failed to delete export');
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return 'N/A';
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Completed':
      case 'completed':
        return 'bg-green-100 text-green-600';
      case 'Processing':
      case 'rendering':
        return 'bg-blue-100 text-blue-600';
      case 'Failed':
        return 'bg-red-100 text-red-600';
      default:
        return 'bg-gray-100 text-gray-600';
    }
  };

  const getFormatIcon = (format) => {
    switch (format) {
      case 'MP4':
      case 'WebM':
        return FileVideo;
      case 'GIF':
        return Image;
      case 'Lottie JSON':
        return File;
      default:
        return File;
    }
  };

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Exports</h1>
          <p className="text-gray-600">Manage your exported motion graphics and download files</p>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200 mb-8">
          <button
            onClick={() => setActiveTab('history')}
            className={`py-3 px-6 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'history'
                ? 'text-orange-600 border-orange-500'
                : 'text-gray-600 border-transparent hover:text-gray-900'
            }`}
          >
            Export History
          </button>
          <button
            onClick={() => setActiveTab('formats')}
            className={`py-3 px-6 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'formats'
                ? 'text-orange-600 border-orange-500'
                : 'text-gray-600 border-transparent hover:text-gray-900'
            }`}
          >
            Export Options
          </button>
        </div>

        {activeTab === 'history' && (
          loading ? (
            <div className="flex justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
            </div>
          ) : exports.length === 0 ? (
            <div className="text-center py-12">
              <Download className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No exports yet</h3>
              <p className="text-gray-600">Start creating and exporting your motion graphics</p>
            </div>
          ) : (
            <div className="space-y-4">
              {exports.map((exportItem) => {
                const FormatIcon = getFormatIcon(exportItem.format);
                
                return (
                  <div
                    key={exportItem.id}
                    className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="flex-shrink-0">
                          <div className="w-12 h-12 bg-gradient-to-r from-orange-100 to-red-100 rounded-xl flex items-center justify-center">
                            <FormatIcon className="w-6 h-6 text-orange-600" />
                          </div>
                        </div>
                        
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-gray-900">
                            {exportItem.template_id || 'Animation Export'}
                          </h3>
                          <div className="flex items-center space-x-4 text-sm text-gray-600 mt-1">
                            <span>{exportItem.format}</span>
                            <span>•</span>
                            <span>{exportItem.resolution}</span>
                            <span>•</span>
                            <span>{formatFileSize(exportItem.file_size)}</span>
                            {exportItem.has_watermark && (
                              <>
                                <span>•</span>
                                <span className="text-orange-600">Watermarked</span>
                              </>
                            )}
                          </div>
                          <div className="flex items-center space-x-2 mt-2">
                            <Calendar className="w-4 h-4 text-gray-400" />
                            <span className="text-sm text-gray-500">
                              {formatDate(exportItem.created_at)}
                            </span>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center space-x-3">
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(exportItem.status)}`}>
                          {exportItem.status}
                        </span>
                        
                        <div className="flex items-center space-x-2">
                          {exportItem.status === 'completed' && exportItem.download_url && (
                            <a
                              href={exportItem.download_url}
                              download
                              className="p-2 text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors"
                            >
                              <Download className="w-4 h-4" />
                            </a>
                          )}
                          
                          {exportItem.status === 'rendering' && (
                            <button className="p-2 text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors">
                              <RefreshCw className="w-4 h-4 animate-spin" />
                            </button>
                          )}
                          
                          <button 
                            onClick={() => handleDeleteExport(exportItem.id)}
                            className="p-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                    
                    {exportItem.error_message && (
                      <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                        <p className="text-sm text-red-600">Error: {exportItem.error_message}</p>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )
        )}

        {activeTab === 'formats' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* MP4 Format */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-gradient-to-r from-blue-100 to-blue-200 rounded-xl flex items-center justify-center mr-4">
                  <FileVideo className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">MP4 Video</h3>
                  <p className="text-sm text-gray-600">Universal video format</p>
                </div>
              </div>
              
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Resolution</label>
                  <select className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500/20">
                    <option>1080p (1920x1080)</option>
                    <option>4K (3840x2160)</option>
                    <option>720p (1280x720)</option>
                    <option>1080p Vertical (1080x1920)</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Frame Rate</label>
                  <select className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500/20">
                    <option>30 FPS</option>
                    <option>60 FPS</option>
                    <option>24 FPS</option>
                  </select>
                </div>
                
                <div className="flex items-center">
                  <input type="checkbox" id="transparent-bg-mp4" className="mr-2" />
                  <label htmlFor="transparent-bg-mp4" className="text-sm text-gray-700">Transparent Background</label>
                </div>
              </div>
            </div>

            {/* WebM Format */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-gradient-to-r from-green-100 to-green-200 rounded-xl flex items-center justify-center mr-4">
                  <FileVideo className="w-6 h-6 text-green-600" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">WebM Video</h3>
                  <p className="text-sm text-gray-600">Web-optimized with alpha</p>
                </div>
              </div>
              
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Quality</label>
                  <select className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500/20">
                    <option>High Quality</option>
                    <option>Medium Quality</option>
                    <option>Web Optimized</option>
                  </select>
                </div>
                
                <div className="flex items-center">
                  <input type="checkbox" id="alpha-channel" className="mr-2" defaultChecked />
                  <label htmlFor="alpha-channel" className="text-sm text-gray-700">Alpha Channel Support</label>
                </div>
              </div>
            </div>

            {/* GIF Format */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-gradient-to-r from-purple-100 to-purple-200 rounded-xl flex items-center justify-center mr-4">
                  <Image className="w-6 h-6 text-purple-600" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Animated GIF</h3>
                  <p className="text-sm text-gray-600">Perfect for social media</p>
                </div>
              </div>
              
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Size</label>
                  <select className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500/20">
                    <option>Original Size</option>
                    <option>720p</option>
                    <option>480p</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Colors</label>
                  <select className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500/20">
                    <option>256 Colors</option>
                    <option>128 Colors</option>
                    <option>64 Colors</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Lottie JSON Format */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-gradient-to-r from-orange-100 to-orange-200 rounded-xl flex items-center justify-center mr-4">
                  <File className="w-6 h-6 text-orange-600" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Lottie JSON</h3>
                  <p className="text-sm text-gray-600">Vector animation for web</p>
                </div>
              </div>
              
              <div className="space-y-3">
                <div className="flex items-center">
                  <input type="checkbox" id="minify-json" className="mr-2" defaultChecked />
                  <label htmlFor="minify-json" className="text-sm text-gray-700">Minify JSON</label>
                </div>
                
                <div className="flex items-center">
                  <input type="checkbox" id="include-assets" className="mr-2" />
                  <label htmlFor="include-assets" className="text-sm text-gray-700">Include External Assets</label>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Storage Info */}
        {user && (
          <div className="mt-8 bg-gradient-to-r from-orange-50 to-red-50 border border-orange-200/50 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Current Plan</h3>
                <p className="text-gray-600">Exports are stored for 30 days before automatic deletion</p>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-gray-900 capitalize">{user.subscription_tier}</div>
                <div className="text-sm text-gray-600">{user.credits_remaining} credits left</div>
              </div>
            </div>
            
            <div className="mt-4">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-orange-500 to-red-500 h-2 rounded-full transition-all duration-300" 
                  style={{ 
                    width: `${Math.max(10, (user.credits_remaining / (user.subscription_tier === 'free' ? 5 : user.subscription_tier === 'mid' ? 50 : 100)) * 100)}%` 
                  }}
                ></div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ExportsPage;