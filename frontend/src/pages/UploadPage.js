import React, { useState, useRef } from 'react';
import { Upload, Link, CheckCircle, XCircle, Loader } from 'lucide-react';
import { apiService } from '../services/api';
import { renderLottiePreview } from '../components/editor/LottieRenderer';

const UploadPage = () => {
  const [dragActive, setDragActive] = useState(false);
  const [urlInput, setUrlInput] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const fileInputRef = useRef(null);

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
      handleFiles(Array.from(e.dataTransfer.files));
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files) {
      handleFiles(Array.from(e.target.files));
    }
  };

  const handleFiles = async (files) => {
    setIsProcessing(true);
    
    const validFiles = files.filter(file =>
      file.name.toLowerCase().endsWith('.json') || file.name.toLowerCase().endsWith('.lottie')
    );

    if (validFiles.length === 0) {
      alert('Please upload .json or .lottie files only');
      setIsProcessing(false);
      return;
    }

    for (const file of validFiles) {
      try {
        const result = await processFile(file, 'upload');
        setUploadedFiles(prev => [...prev, result]);
      } catch (error) {
        console.error('File processing error:', error);
        setUploadedFiles(prev => [...prev, {
          id: Date.now() + Math.random(),
          name: file.name,
          status: 'error',
          error: error.message
        }]);
      }
    }
    
    setIsProcessing(false);
  };

  const handleUrlImport = async () => {
    if (!urlInput.trim()) return;

    setIsProcessing(true);
    try {
      const result = await apiService.importFromUrl(urlInput);
      setUploadedFiles(prev => [...prev, result]);
      setUrlInput('');
    } catch (error) {
      console.error('URL import error:', error);
      alert('Import failed. Please try again.');
      setUploadedFiles(prev => [...prev, {
        id: Date.now() + Math.random(),
        name: urlInput,
        status: 'error',
        error: error.message
      }]);
    }
    setIsProcessing(false);
  };

  const processFile = async (file, source) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('source', source);
    let result;
    try {
      result = await apiService.uploadTemplate(formData);
    } catch (error) {
      alert('Upload failed. Please try again.');
      throw error;
    }

    // Generate previews client-side: last-frame PNG + 2.5s WebM
    try {
      const backendBase = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
      // Fetch animation data to render locally
      const animData = await apiService.getTemplateData(result.id);
      const { webmBlob, pngBlob } = await renderLottiePreview({
        animationData: animData,
        width: 400,
        height: 400,
        durationSeconds: 2.5,
        fps: 30
      });

      await apiService.uploadTemplatePreviews(result.id, {
        imageFile: new File([pngBlob], `${result.id}_thumb.png`, { type: 'image/png' }),
        videoFile: new File([webmBlob], `${result.id}_preview.webm`, { type: 'video/webm' })
      });
    } catch (e) {
      console.warn('Preview generation failed (continuing without):', e);
    }

    return {
      id: result.id,
      name: result.name,
      status: 'success',
      templateId: result.id,
      preview: result.preview_url,
      manifest: result.manifest
    };
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'error':
        return <XCircle className="w-5 h-5 text-red-600" />;
      case 'processing':
        return <Loader className="w-5 h-5 text-blue-600 animate-spin" />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Upload Templates</h1>
          <p className="text-gray-600">Import .json and .lottie files to create editable motion graphics templates</p>
        </div>

        {/* File Upload Area */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 mb-6">
          <div
            className={`border-2 border-dashed rounded-xl p-12 text-center transition-colors ${
              dragActive 
                ? 'border-orange-500 bg-orange-50' 
                : 'border-gray-300 hover:border-orange-400 hover:bg-orange-50'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <Upload className="w-12 h-12 text-orange-500 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Drop your files here
            </h3>
            <p className="text-gray-600 mb-6">
              Supports .json (Lottie/Bodymovin) and .lottie files
            </p>
            
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".json,.lottie"
              onChange={handleFileInput}
              className="hidden"
            />
            
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isProcessing}
              className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-orange-500 to-red-500 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-orange-500/25 transition-all duration-200 disabled:opacity-50"
            >
              <Upload className="w-5 h-5 mr-2" />
              {isProcessing ? 'Processing...' : 'Choose Files'}
            </button>
          </div>
        </div>

        {/* URL Import */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
          <div className="flex items-center mb-4">
            <Link className="w-6 h-6 text-orange-500 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">Import from URL</h3>
          </div>
          
          <div className="flex gap-3">
            <input
              type="url"
              placeholder="https://example.com/animation.json"
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-300"
            />
            <button
              onClick={handleUrlImport}
              disabled={!urlInput.trim() || isProcessing}
              className="px-6 py-3 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors disabled:opacity-50"
            >
              Import
            </button>
          </div>
        </div>

        {/* Upload Results */}
        {uploadedFiles.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Upload Results</h3>
            
            <div className="space-y-3">
              {uploadedFiles.map((file) => (
                <div key={file.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(file.status)}
                    <div>
                      <p className="font-medium text-gray-900">{file.name}</p>
                      {file.error && (
                        <p className="text-sm text-red-600">{file.error}</p>
                      )}
                    </div>
                  </div>
                  
                  {file.status === 'success' && (
                    <div className="flex items-center space-x-3">
                      {file.preview && (
                        <img 
                          src={file.preview} 
                          alt="Preview" 
                          className="w-12 h-12 object-cover rounded border"
                        />
                      )}
                      <a
                        href={`/t/${file.templateId}`}
                        className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors"
                      >
                        Edit Template
                      </a>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* Supported Formats Info */}
        <div className="mt-8 bg-blue-50 rounded-xl p-6 border border-blue-200">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">Supported Formats</h3>
          <div className="grid md:grid-cols-2 gap-4 text-sm text-blue-800">
            <div>
              <h4 className="font-semibold mb-2">.json Files</h4>
              <ul className="space-y-1">
                <li>• Lottie/Bodymovin exports from After Effects</li>
                <li>• Standard Lottie JSON animations</li>
                <li>• Web-based Lottie animations</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-2">.lottie Files</h4>
              <ul className="space-y-1">
                <li>• dotLottie optimized format</li>
                <li>• Compressed animations with assets</li>
                <li>• Modern Lottie file standard</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;