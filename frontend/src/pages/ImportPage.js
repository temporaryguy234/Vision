import React, { useState } from 'react';
import { Upload, FileVideo, Image, File, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

const ImportPage = () => {
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([
    {
      id: 1,
      name: 'logo-animation.json',
      type: 'Lottie JSON',
      size: '2.1 MB',
      status: 'processing',
      progress: 65
    },
    {
      id: 2,
      name: 'intro-template.mp4',
      type: 'Video',
      size: '45.2 MB',
      status: 'completed',
      progress: 100
    },
    {
      id: 3,
      name: 'social-post.gif',
      type: 'GIF',
      size: '8.7 MB',
      status: 'failed',
      progress: 0,
      error: 'Unsupported GIF format'
    }
  ]);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      // Handle file upload logic here
      console.log('Files dropped:', e.dataTransfer.files);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-600" />;
      case 'processing':
        return <AlertCircle className="w-5 h-5 text-yellow-600" />;
      default:
        return <File className="w-5 h-5 text-gray-600" />;
    }
  };

  const getFileIcon = (type) => {
    if (type.includes('Video') || type.includes('MP4')) {
      return <FileVideo className="w-8 h-8 text-blue-600" />;
    } else if (type.includes('GIF') || type.includes('Image')) {
      return <Image className="w-8 h-8 text-purple-600" />;
    } else {
      return <File className="w-8 h-8 text-gray-600" />;
    }
  };

  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Import Templates</h1>
          <p className="text-gray-600">Upload your own motion graphics templates and add them to your library</p>
        </div>

        {/* Upload Area */}
        <div
          className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 ${
            dragActive
              ? 'border-orange-500 bg-orange-50'
              : 'border-gray-300 bg-gray-50 hover:border-orange-400 hover:bg-orange-50/50'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <div className="space-y-4">
            <div className="w-16 h-16 bg-gradient-to-r from-orange-500 to-red-500 rounded-full flex items-center justify-center mx-auto">
              <Upload className="w-8 h-8 text-white" />
            </div>
            
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Drop files here or click to upload
              </h3>
              <p className="text-gray-600 mb-4">
                Supports Lottie JSON, MP4, GIF, and other motion graphics formats
              </p>
              
              <button className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-orange-500 to-red-500 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-orange-500/25 transition-all duration-200">
                <Upload className="w-5 h-5 mr-2" />
                Choose Files
              </button>
            </div>
          </div>
          
          <input
            type="file"
            multiple
            accept=".json,.mp4,.gif,.webm,.mov"
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            onChange={(e) => {
              if (e.target.files) {
                console.log('Files selected:', e.target.files);
              }
            }}
          />
        </div>

        {/* Supported Formats */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
            <div className="flex items-center mb-4">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-100 to-blue-200 rounded-xl flex items-center justify-center mr-4">
                <FileVideo className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Video Files</h3>
                <p className="text-sm text-gray-600">MP4, WebM, MOV</p>
              </div>
            </div>
            <p className="text-sm text-gray-600">
              Upload your rendered motion graphics videos. We'll automatically extract keyframes and create editable parameters.
            </p>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
            <div className="flex items-center mb-4">
              <div className="w-12 h-12 bg-gradient-to-r from-purple-100 to-purple-200 rounded-xl flex items-center justify-center mr-4">
                <Image className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Animated Images</h3>
                <p className="text-sm text-gray-600">GIF, APNG</p>
              </div>
            </div>
            <p className="text-sm text-gray-600">
              Import animated images and convert them to editable motion graphics with text and style controls.
            </p>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
            <div className="flex items-center mb-4">
              <div className="w-12 h-12 bg-gradient-to-r from-orange-100 to-orange-200 rounded-xl flex items-center justify-center mr-4">
                <File className="w-6 h-6 text-orange-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Animation Data</h3>
                <p className="text-sm text-gray-600">Lottie JSON, AE</p>
              </div>
            </div>
            <p className="text-sm text-gray-600">
              Upload Lottie animations or After Effects projects for full editing capabilities with natural language commands.
            </p>
          </div>
        </div>

        {/* Upload History */}
        {uploadedFiles.length > 0 && (
          <div className="mt-8">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Recent Uploads</h3>
            <div className="space-y-4">
              {uploadedFiles.map((file) => (
                <div key={file.id} className="bg-white rounded-xl p-6 shadow-lg border border-gray-200">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="flex-shrink-0">
                        {getFileIcon(file.type)}
                      </div>
                      
                      <div className="flex-1">
                        <h4 className="font-semibold text-gray-900">{file.name}</h4>
                        <div className="flex items-center space-x-4 text-sm text-gray-600 mt-1">
                          <span>{file.type}</span>
                          <span>•</span>
                          <span>{file.size}</span>
                        </div>
                        
                        {file.status === 'processing' && (
                          <div className="mt-3">
                            <div className="flex items-center justify-between text-sm text-gray-600 mb-1">
                              <span>Processing...</span>
                              <span>{file.progress}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div
                                className="bg-gradient-to-r from-orange-500 to-red-500 h-2 rounded-full transition-all duration-300"
                                style={{ width: `${file.progress}%` }}
                              />
                            </div>
                          </div>
                        )}
                        
                        {file.error && (
                          <div className="mt-2 text-sm text-red-600">
                            Error: {file.error}
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center space-x-3">
                      {getStatusIcon(file.status)}
                      
                      {file.status === 'completed' && (
                        <button className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors">
                          Add to Library
                        </button>
                      )}
                      
                      {file.status === 'failed' && (
                        <button className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
                          Retry
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Import Guidelines */}
        <div className="mt-8 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200/50 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Import Guidelines</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Best Practices</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Keep file sizes under 100MB for faster processing</li>
                <li>• Use descriptive filenames for easy organization</li>
                <li>• Include preview images when possible</li>
                <li>• Organize similar templates in folders</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Technical Requirements</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Maximum resolution: 4K (3840x2160)</li>
                <li>• Supported frame rates: 24, 30, 60 FPS</li>
                <li>• Lottie files should be valid JSON format</li>
                <li>• Videos should use standard codecs (H.264, VP9)</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ImportPage;