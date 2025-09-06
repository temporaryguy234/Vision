import React, { useState, useCallback } from 'react';
import { Upload, FileVideo, Image, File, CheckCircle, XCircle, AlertCircle, Plus, Edit } from 'lucide-react';
import { apiService } from '../services/api';

const ImportPage = () => {
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  
  // Wizard state
  const [showWizard, setShowWizard] = useState(false);
  const [wizardData, setWizardData] = useState([]);
  const [wizardStep, setWizardStep] = useState(0);

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
      handleFileUpload(Array.from(e.dataTransfer.files));
    }
  };
  
  const handleFileUpload = async (files) => {
    if (!files || files.length === 0) return;
    
    setIsUploading(true);
    
    try {
      const formData = new FormData();
      files.forEach(file => {
        formData.append('files', file);
      });
      
      // Upload files
      const response = await apiService.bulkImportUpload(formData);
      
      // Process results
      const processedFiles = response.results.map((result, index) => ({
        id: Date.now() + index,
        name: result.filename,
        type: result.asset_type || 'Unknown',
        size: formatFileSize(result.metadata?.file_size || files[index].size),
        status: result.status,
        file_url: result.file_url,
        thumbnail_url: result.thumbnail_url,
        metadata: result.metadata,
        file_hash: result.file_hash,
        error: result.message
      }));
      
      setUploadedFiles(prev => [...prev, ...processedFiles]);
      
      // Show wizard for successful uploads
      const successfulUploads = processedFiles.filter(f => f.status === 'success');
      if (successfulUploads.length > 0) {
        setWizardData(successfulUploads);
        setShowWizard(true);
      }
      
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Upload failed. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };
  
  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };
  
  const handleCreateTemplates = async () => {
    try {
      const createData = {
        items: wizardData.map(item => ({
          filename: item.name,
          title: item.templateTitle || item.name.replace(/\.[^/.]+$/, ""),
          category: item.category || "MISCELLANEOUS",
          tags: item.tags ? item.tags.split(',').map(tag => tag.trim()) : [],
          thumbnail_url: item.thumbnail_url || "",
          creator_id: "current_user",
          is_public: item.is_public !== false,
          file_url: item.file_url,
          asset_type: item.type,
          metadata: item.metadata,
          file_hash: item.file_hash
        }))
      };
      
      const response = await apiService.bulkImportCreateTemplates(createData);
      
      if (response.templates_created.length > 0) {
        alert(`Successfully created ${response.templates_created.length} templates!`);
        setShowWizard(false);
        setWizardData([]);
        
        // Update uploaded files status
        setUploadedFiles(prev => prev.map(file => {
          const created = response.templates_created.find(t => t.filename === file.name);
          if (created) {
            return { ...file, status: 'template_created', template_id: created.template_id };
          }
          return file;
        }));
      }
      
      if (response.errors.length > 0) {
        console.error('Template creation errors:', response.errors);
      }
      
    } catch (error) {
      console.error('Template creation failed:', error);
      alert('Failed to create templates. Please try again.');
    }
  };

  const handleLottieFilesImport = (result) => {
    // Add to upload history as successfully created template
    const newFile = {
      id: Date.now(),
      name: result.template_title,
      type: 'Lottie JSON',
      size: 'From LottieFiles',
      status: 'template_created',
      template_id: result.template_id,
      category: result.category
    };
    
    setUploadedFiles(prev => [newFile, ...prev]);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
      case 'completed':
      case 'template_created':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'error':
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-600" />;
      case 'duplicate':
        return <AlertCircle className="w-5 h-5 text-yellow-600" />;
      case 'processing':
        return <AlertCircle className="w-5 h-5 text-blue-600" />;
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Import Motion Graphics</h1>
          <p className="text-gray-600">Upload your motion graphics files from any tool - After Effects, Photoshop, web tools, or any other software</p>
        </div>
        {/* Upload Area */}

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
              
              <button 
                className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-orange-500 to-red-500 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-orange-500/25 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={isUploading}
              >
                <Upload className="w-5 h-5 mr-2" />
                {isUploading ? 'Uploading...' : 'Choose Files'}
              </button>
            </div>
          </div>
          
          <input
            type="file"
            multiple
            accept=".json,.lottie,.mp4,.webm,.mov,.avi,.gif,.apng,.png,.jpg,.jpeg,.svg,.aep,.prproj,.blend,.c4d"
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            disabled={isUploading}
            onChange={(e) => {
              if (e.target.files) {
                handleFileUpload(Array.from(e.target.files));
              }
            }}
          />
        </div>

        {/* Supported Motion Graphics Formats */}
        <div className="mt-8">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Supported Motion Graphics Formats</h3>
          
          <div className="grid md:grid-cols-3 gap-6">
            {/* Animation Files */}
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-6 rounded-xl border border-blue-100">
              <div className="flex items-center mb-3">
                <FileVideo className="w-6 h-6 text-blue-600 mr-2" />
                <h4 className="font-semibold text-gray-900">Animation Files</h4>
              </div>
              <ul className="text-sm text-gray-700 space-y-1">
                <li>• <strong>Lottie JSON</strong> - From After Effects Bodymovin</li>
                <li>• <strong>Video</strong> - MP4, WebM, MOV, AVI</li>
                <li>• <strong>GIF</strong> - From Photoshop or web tools</li>
                <li>• <strong>APNG</strong> - Animated PNG sequences</li>
              </ul>
            </div>

            {/* Design Files */}
            <div className="bg-gradient-to-br from-green-50 to-emerald-50 p-6 rounded-xl border border-green-100">
              <div className="flex items-center mb-3">
                <Image className="w-6 h-6 text-green-600 mr-2" />
                <h4 className="font-semibold text-gray-900">Design Files</h4>
              </div>
              <ul className="text-sm text-gray-700 space-y-1">
                <li>• <strong>SVG</strong> - Vector animations</li>
                <li>• <strong>PNG/JPG</strong> - Static images</li>
                <li>• <strong>Image Sequences</strong> - Multiple PNGs</li>
                <li>• <strong>Vector Graphics</strong> - Scalable designs</li>
              </ul>
            </div>

            {/* Project Files */}
            <div className="bg-gradient-to-br from-purple-50 to-violet-50 p-6 rounded-xl border border-purple-100">
              <div className="flex items-center mb-3">
                <File className="w-6 h-6 text-purple-600 mr-2" />
                <h4 className="font-semibold text-gray-900">Project Files</h4>
              </div>
              <ul className="text-sm text-gray-700 space-y-1">
                <li>• <strong>After Effects</strong> - .aep project files</li>
                <li>• <strong>Premiere Pro</strong> - .prproj timeline files</li>
                <li>• <strong>Blender</strong> - .blend 3D animations</li>
                <li>• <strong>Cinema 4D</strong> - .c4d motion graphics</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Bulk Import Wizard Modal */}
        {showWizard && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6 border-b border-gray-200">
                <h2 className="text-2xl font-bold text-gray-900">Create Templates</h2>
                <p className="text-gray-600 mt-1">
                  Review and customize your templates before adding them to the library
                </p>
              </div>
              
              <div className="p-6 space-y-6">
                {wizardData.map((item, index) => (
                  <div key={index} className="border border-gray-200 rounded-xl p-6">
                    <div className="flex items-start space-x-4">
                      <img
                        src={item.thumbnail_url || "https://via.placeholder.com/100x80?text=No+Preview"}
                        alt="Preview"
                        className="w-20 h-16 object-cover rounded-lg border border-gray-200"
                      />
                      
                      <div className="flex-1 space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Template Title
                            </label>
                            <input
                              type="text"
                              value={item.templateTitle || item.name.replace(/\.[^/.]+$/, "")}
                              onChange={(e) => {
                                const newData = [...wizardData];
                                newData[index] = { ...newData[index], templateTitle: e.target.value };
                                setWizardData(newData);
                              }}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-300"
                            />
                          </div>
                          
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Category
                            </label>
                            <select
                              value={item.category || "MISCELLANEOUS"}
                              onChange={(e) => {
                                const newData = [...wizardData];
                                newData[index] = { ...newData[index], category: e.target.value };
                                setWizardData(newData);
                              }}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-300"
                            >
                              <option value="INTROS_OUTROS">Intros & Outros</option>
                              <option value="LOWER_THIRDS">Lower Thirds</option>
                              <option value="TITLES_QUOTES">Titles & Quotes</option>
                              <option value="CHARTS_MAPS">Charts & Maps</option>
                              <option value="SOCIAL_MEDIA">Social Media Posts</option>
                              <option value="ADS_PROMOS">Ads & Promos</option>
                              <option value="OVERLAYS">Overlays</option>
                              <option value="ANIMATED_ICONS">Animated Icons</option>
                              <option value="MISCELLANEOUS">Miscellaneous</option>
                            </select>
                          </div>
                        </div>
                        
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Tags (comma-separated)
                          </label>
                          <input
                            type="text"
                            value={item.tags || ""}
                            onChange={(e) => {
                              const newData = [...wizardData];
                              newData[index] = { ...newData[index], tags: e.target.value };
                              setWizardData(newData);
                            }}
                            placeholder="animation, logo, intro"
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-300"
                          />
                        </div>
                        
                        <div className="flex items-center">
                          <input
                            type="checkbox"
                            id={`public-${index}`}
                            checked={item.is_public !== false}
                            onChange={(e) => {
                              const newData = [...wizardData];
                              newData[index] = { ...newData[index], is_public: e.target.checked };
                              setWizardData(newData);
                            }}
                            className="w-4 h-4 text-orange-600 bg-gray-100 border-gray-300 rounded focus:ring-orange-500"
                          />
                          <label htmlFor={`public-${index}`} className="ml-2 text-sm text-gray-700">
                            Make this template public
                          </label>
                        </div>
                        
                        <div className="text-sm text-gray-500">
                          <span className="font-medium">Type:</span> {item.type} •{' '}
                          <span className="font-medium">Size:</span> {item.size}
                          {item.metadata?.width && item.metadata?.height && (
                            <> • <span className="font-medium">Dimensions:</span> {item.metadata.width}×{item.metadata.height}</>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="p-6 border-t border-gray-200 flex items-center justify-between">
                <button
                  onClick={() => setShowWizard(false)}
                  className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                
                <button
                  onClick={handleCreateTemplates}
                  className="px-6 py-2 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-lg hover:shadow-lg hover:shadow-orange-500/25 transition-all duration-200"
                >
                  Create {wizardData.length} Template{wizardData.length !== 1 ? 's' : ''}
                </button>
              </div>
            </div>
          </div>
        )}

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
                        
                        {file.status === 'duplicate' && (
                          <div className="mt-2 text-sm text-yellow-600">
                            This file already exists in the library
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center space-x-3">
                      {getStatusIcon(file.status)}
                      
                      {file.status === 'success' && (
                        <button 
                          onClick={() => {
                            setWizardData([file]);
                            setShowWizard(true);
                          }}
                          className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors"
                        >
                          Create Template
                        </button>
                      )}
                      
                      {file.status === 'template_created' && (
                        <button 
                          onClick={() => window.open(`/editor/${file.template_id}`, '_blank')}
                          className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
                        >
                          Edit Template
                        </button>
                      )}
                      
                      {file.status === 'duplicate' && (
                        <button className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
                          View Existing
                        </button>
                      )}
                      
                      {file.status === 'error' && (
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