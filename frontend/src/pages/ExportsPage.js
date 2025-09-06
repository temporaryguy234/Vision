import React, { useState } from 'react';
import { Download, Calendar, FileVideo, Image, File, Eye, Trash2, RefreshCw } from 'lucide-react';

const ExportsPage = () => {
  const [activeTab, setActiveTab] = useState('history');

  const exports = [
    {
      id: 1,
      projectName: 'Summer Campaign Video',
      format: 'MP4',
      resolution: '1080p',
      size: '45.2 MB',
      duration: '15s',
      status: 'Completed',
      exportedAt: '2024-01-15 14:30',
      downloadUrl: '#'
    },
    {
      id: 2,
      projectName: 'Q4 Sales Report',
      format: 'WebM',
      resolution: '4K',
      size: '128.7 MB',
      duration: '30s',
      status: 'Completed',
      exportedAt: '2024-01-14 09:15',
      downloadUrl: '#'
    },
    {
      id: 3,
      projectName: 'Brand Logo Animation',
      format: 'GIF',
      resolution: '720p',
      size: '12.4 MB',
      duration: '8s',
      status: 'Processing',
      exportedAt: '2024-01-13 16:45',
      downloadUrl: null
    },
    {
      id: 4,
      projectName: 'Product Launch Teaser',
      format: 'Lottie JSON',
      resolution: 'Vector',
      size: '2.1 MB',
      duration: '12s',
      status: 'Completed',
      exportedAt: '2024-01-12 11:20',
      downloadUrl: '#'
    },
    {
      id: 5,
      projectName: 'Motivational Quote Card',
      format: 'MP4',
      resolution: '1080p Vertical',
      size: '18.9 MB',
      duration: '6s',
      status: 'Failed',
      exportedAt: '2024-01-11 13:05',
      downloadUrl: null,
      error: 'Insufficient storage space'
    }
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'Completed':
        return 'bg-green-100 text-green-600';
      case 'Processing':
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
                        <h3 className="text-lg font-semibold text-gray-900">{exportItem.projectName}</h3>
                        <div className="flex items-center space-x-4 text-sm text-gray-600 mt-1">
                          <span>{exportItem.format}</span>
                          <span>•</span>
                          <span>{exportItem.resolution}</span>
                          <span>•</span>
                          <span>{exportItem.size}</span>
                          <span>•</span>
                          <span>{exportItem.duration}</span>
                        </div>
                        <div className="flex items-center space-x-2 mt-2">
                          <Calendar className="w-4 h-4 text-gray-400" />
                          <span className="text-sm text-gray-500">{exportItem.exportedAt}</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-3">
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(exportItem.status)}`}>
                        {exportItem.status}
                      </span>
                      
                      <div className="flex items-center space-x-2">
                        {exportItem.status === 'Completed' && exportItem.downloadUrl && (
                          <>
                            <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
                              <Eye className="w-4 h-4" />
                            </button>
                            <button className="p-2 text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors">
                              <Download className="w-4 h-4" />
                            </button>
                          </>
                        )}
                        
                        {exportItem.status === 'Processing' && (
                          <button className="p-2 text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors">
                            <RefreshCw className="w-4 h-4 animate-spin" />
                          </button>
                        )}
                        
                        {exportItem.status === 'Failed' && (
                          <button className="p-2 text-orange-600 hover:text-orange-700 hover:bg-orange-50 rounded-lg transition-colors">
                            <RefreshCw className="w-4 h-4" />
                          </button>
                        )}
                        
                        <button className="p-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                  
                  {exportItem.error && (
                    <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                      <p className="text-sm text-red-600">Error: {exportItem.error}</p>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
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
        <div className="mt-8 bg-gradient-to-r from-orange-50 to-red-50 border border-orange-200/50 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Storage Usage</h3>
              <p className="text-gray-600">Exports are stored for 30 days before automatic deletion</p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-gray-900">2.4 GB</div>
              <div className="text-sm text-gray-600">of 10 GB used</div>
            </div>
          </div>
          
          <div className="mt-4">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-gradient-to-r from-orange-500 to-red-500 h-2 rounded-full" style={{ width: '24%' }}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExportsPage;