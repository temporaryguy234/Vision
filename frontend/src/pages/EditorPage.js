import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { Play, Pause, RotateCcw, Save, Settings, Zap, Download } from 'lucide-react';
import { apiService } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import Canvas from '../components/editor/Canvas';
import PropertiesPanel from '../components/editor/PropertiesPanel';
import ExportModal from '../components/editor/ExportModal';
import SubscriptionModal from '../components/subscription/SubscriptionModal';

const EditorPage = () => {
  const { templateId } = useParams();
  const [template, setTemplate] = useState(null);
  const [animationData, setAnimationData] = useState(null);
  const [currentState, setCurrentState] = useState({});
  const [isPlaying, setIsPlaying] = useState(false);
  const [speed, setSpeed] = useState(1.0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showDebug, setShowDebug] = useState(false);
  const [promptText, setPromptText] = useState('');
  const [promptLoading, setPromptLoading] = useState(false);
  const [showSubscription, setShowSubscription] = useState(false);
  const [showExportModal, setShowExportModal] = useState(false);
  const [exportLoading, setExportLoading] = useState(false);
  
  // Editor state management
  const [editorState, setEditorState] = useState({
    canvas: {
      background_color: '#FFFFFF',
      width: 400,
      height: 400,
      global_playback_speed: 1.0
    },
    elements: {}
  });
  const [selectedElements, setSelectedElements] = useState([]);
  const [zoom, setZoom] = useState(1.0);
  const [activeTab, setActiveTab] = useState('Properties');
  const [commandInput, setCommandInput] = useState('');
  
  const { user } = useAuth();
  const canvasRef = useRef();

  // Load template data
  useEffect(() => {
    loadTemplate();
  }, [templateId]);

  const loadTemplate = async () => {
    try {
      setLoading(true);
      const templateData = await apiService.get(`/templates/${templateId}`);
      setTemplate(templateData);
      
      // Load animation data
      const animData = await apiService.get(`/templates/${templateId}/data`);
      setAnimationData(animData);
      
      // Initialize editor state from template
      if (templateData.editable_parameters_schema) {
        setEditorState(prev => ({
          ...prev,
          canvas: {
            ...prev.canvas,
            ...templateData.editable_parameters_schema.canvas
          }
        }));
      }
      
      // Initialize elements from manifest
      if (templateData.manifest && templateData.manifest.elements) {
        const elements = {};
        templateData.manifest.elements.forEach(element => {
          elements[element.id] = {
            ...element.parameters,
            ...element.defaults
          };
        });
        setEditorState(prev => ({
          ...prev,
          elements
        }));
      }
      
    } catch (err) {
      console.error('Failed to load template:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      await apiService.post(`/templates/${templateId}/revisions`, {
        template_id: templateId,
        user_id: user?.id,
        state: currentState,
        animation_data: animationData
      });
      alert('Saved successfully!');
    } catch (err) {
      console.error('Save failed:', err);
      alert('Failed to save. Please try again.');
    }
  };

  const handleExport = async (format, resolution) => {
    try {
      setExportLoading(true);
      const result = await apiService.post('/exports/create', {
        template_id: templateId,
        current_state: currentState,
        export_format: format,
        resolution: resolution
      });
      
      if (result.download_url) {
        window.open(result.download_url, '_blank');
      } else {
        alert('Export started! You will be notified when ready.');
      }
    } catch (err) {
      console.error('Export failed:', err);
      if (err.status === 402) {
        setShowSubscription(true);
      } else {
        alert('Export failed. Please try again.');
      }
    } finally {
      setExportLoading(false);
      setShowExportModal(false);
    }
  };

  const applyPatchesToAnimation = (patches, manifest, animationData) => {
    if (!patches || !animationData) return null;
    
    const updated = JSON.parse(JSON.stringify(animationData));
    
    for (const patch of patches) {
      if (patch.op === 'replace') {
        const pathParts = patch.path.split('/').filter(p => p);
        let current = updated;
        
        for (let i = 0; i < pathParts.length - 1; i++) {
          if (current[pathParts[i]] === undefined) {
            current[pathParts[i]] = {};
          }
          current = current[pathParts[i]];
        }
        
        if (pathParts.length > 0) {
          current[pathParts[pathParts.length - 1]] = patch.value;
        }
      }
    }

    return updated;
  };

  const handlePrompt = async () => {
    if (!promptText.trim()) return;

    try {
      setPromptLoading(true);
      
      const response = await apiService.post(`/templates/${templateId}/prompt`, {
        prompt: promptText,
        state: currentState,
        manifest: template?.manifest || {}
      });

      // Apply patches from AI response
      if (response.patches && response.patches.length > 0) {
        const newState = { ...currentState };
        response.patches.forEach(patch => {
          if (patch.op === 'replace') {
            const pathParts = patch.path.split('/').filter(p => p);
            if (pathParts.length > 0) newState[pathParts.join('.')] = patch.value;
          }
        });
        setCurrentState(newState);

        // Apply directly to animation JSON
        const updatedAnim = applyPatchesToAnimation(response.patches, template?.manifest || {}, animationData);
        if (updatedAnim) setAnimationData(updatedAnim);
        
        // Clear prompt
        setPromptText('');
        
        // Show success
        alert(`Applied ${response.patches.length} changes from prompt`);
      }

    } catch (err) {
      console.error('Prompt processing failed:', err);
      alert('Failed to process prompt. Please try again.');
    } finally {
      setPromptLoading(false);
    }
  };

  const handleSpeedChange = (newSpeed) => {
    setSpeed(newSpeed);
    setCurrentState(prev => ({ ...prev, speed: newSpeed }));
  };

  // Editor event handlers
  const handleElementSelect = (elementId, multiSelect = false) => {
    if (!elementId) {
      setSelectedElements([]);
      return;
    }
    
    if (multiSelect) {
      setSelectedElements(prev => 
        prev.includes(elementId) 
          ? prev.filter(id => id !== elementId)
          : [...prev, elementId]
      );
    } else {
      setSelectedElements([elementId]);
    }
  };

  const handleElementTransform = (elementId, transform) => {
    setEditorState(prev => ({
      ...prev,
      elements: {
        ...prev.elements,
        [elementId]: {
          ...prev.elements[elementId],
          ...transform
        }
      }
    }));
  };

  const handlePropertyChange = (elementId, property, value) => {
    setEditorState(prev => ({
      ...prev,
      elements: {
        ...prev.elements,
        [elementId]: {
          ...prev.elements[elementId],
          [property]: value
        }
      }
    }));
  };

  const handleCanvasChange = (property, value, oldValue) => {
    setEditorState(prev => ({
      ...prev,
      canvas: {
        ...prev.canvas,
        [property]: value
      }
    }));
  };

  const handleCommandInputChange = (value) => {
    setCommandInput(value);
  };

  const handleCommandSubmit = () => {
    if (commandInput.trim()) {
      setPromptText(commandInput);
      handlePrompt();
      setCommandInput('');
    }
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
  };

  const handleApplyBrandKit = (brandKit) => {
    // Apply brand kit colors to selected elements
    selectedElements.forEach(elementId => {
      if (brandKit.colors.length > 0) {
        handlePropertyChange(elementId, 'color', brandKit.colors[0]);
      }
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading template...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Template</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => window.history.back()}
            className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Main Editor Area */}
      <div className="flex-1 flex flex-col">
        {/* Top Toolbar */}
        <div className="bg-white border-b border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h1 className="text-xl font-semibold text-gray-900">
                {template?.title || 'Untitled Template'}
              </h1>
              
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setIsPlaying(!isPlaying)}
                  className="p-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600"
                >
                  {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
                </button>
                
                <button
                  onClick={() => setSpeed(1.0)}
                  className="p-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                >
                  <RotateCcw className="w-5 h-5" />
                </button>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={handleSave}
                className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 flex items-center"
              >
                <Save className="w-4 h-4 mr-2" />
                Save
              </button>
              
              <button
                onClick={() => setShowExportModal(true)}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center"
              >
                <Download className="w-4 h-4 mr-2" />
                Export
              </button>
              
              <button
                onClick={() => setShowDebug(!showDebug)}
                className="p-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
              >
                <Settings className="w-5 h-5" />
              </button>
            </div>
          </div>
          
          {/* Speed Control */}
          <div className="mt-4 flex items-center space-x-4">
            <label className="text-sm font-medium text-gray-700">Speed:</label>
            <input
              type="range"
              min="0.2"
              max="3.0"
              step="0.1"
              value={speed}
              onChange={(e) => handleSpeedChange(parseFloat(e.target.value))}
              className="flex-1 max-w-xs"
            />
            <span className="text-sm font-medium text-gray-900 w-12">{speed.toFixed(1)}x</span>
          </div>
        </div>
        
        {/* Canvas Area */}
        <div className="flex-1 flex items-center justify-center p-8 bg-gray-100">
          <Canvas
            ref={canvasRef}
            template={template}
            editorState={editorState}
            selectedElements={selectedElements}
            zoom={zoom}
            isPlaying={isPlaying}
            onElementSelect={handleElementSelect}
            onElementTransform={handleElementTransform}
            onCanvasChange={handleCanvasChange}
          />
        </div>
        
        {/* Prompt Box */}
        <div className="border-t border-gray-200 p-4 bg-white">
          <div className="flex items-center space-x-3">
            <Zap className="w-5 h-5 text-orange-500" />
            <input
              type="text"
              placeholder="Try: 'make it 30% faster', 'change title to Hello World', 'set primary color to #FF6A00'"
              value={promptText}
              onChange={(e) => setPromptText(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handlePrompt()}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-300"
            />
            <button
              onClick={handlePrompt}
              disabled={!promptText.trim() || promptLoading}
              className="px-6 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 disabled:opacity-50"
            >
              {promptLoading ? 'Processing...' : 'Apply'}
            </button>
          </div>
        </div>
      </div>
      
      {/* Right Panel - Properties */}
      <div className="w-80 bg-white border-l border-gray-200 flex flex-col">
        <PropertiesPanel
          template={template}
          editorState={editorState}
          selectedElements={selectedElements}
          activeTab={activeTab}
          commandInput={commandInput}
          onTabChange={handleTabChange}
          onCommandInputChange={handleCommandInputChange}
          onCommandSubmit={handleCommandSubmit}
          onPropertyChange={handlePropertyChange}
          onCanvasChange={handleCanvasChange}
          onApplyBrandKit={handleApplyBrandKit}
          brandKits={[]}
        />
      </div>
      
      {/* Export Modal */}
      <ExportModal
        isOpen={showExportModal}
        onClose={() => setShowExportModal(false)}
        onExport={handleExport}
        loading={exportLoading}
      />
      
      {/* Subscription Modal */}
      <SubscriptionModal
        isOpen={showSubscription}
        onClose={() => setShowSubscription(false)}
      />
      
      {/* Debug Panel */}
      {showDebug && (
        <div className="fixed bottom-4 right-4 w-96 bg-white border border-gray-300 rounded-lg shadow-lg p-4 max-h-80 overflow-y-auto">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-gray-900">DEBUG</h3>
            <button
              onClick={() => setShowDebug(false)}
              className="text-gray-500 hover:text-gray-700"
            >
              ×
            </button>
          </div>
          
          <div className="space-y-3 text-xs">
            <div>
              <h4 className="font-medium text-gray-700">Template ID:</h4>
              <p className="text-gray-600 font-mono">{templateId}</p>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-700">User:</h4>
              <p className="text-gray-600">{user ? user.email : 'Not signed in'}</p>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-700">Animation Loaded:</h4>
              <p className="text-gray-600">{animationData ? 'Yes' : 'No'}</p>
            </div>

            {animationData && (
              <div>
                <h4 className="font-medium text-gray-700">Animation Info:</h4>
                <p className="text-gray-600">
                  {animationData.w}x{animationData.h}, {animationData.fr}fps, {animationData.layers?.length || 0} layers
                </p>
              </div>
            )}
            
            <div>
              <h4 className="font-medium text-gray-700">Current State:</h4>
              <pre className="text-gray-600 bg-gray-50 p-2 rounded overflow-x-auto">
                {JSON.stringify(currentState, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      )}
      
    </div>
  );
};

export default EditorPage;