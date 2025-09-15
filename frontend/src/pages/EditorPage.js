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
      try {
        const animData = await apiService.get(`/templates/${templateId}/data`);
        setAnimationData(animData);
        console.log('Animation data loaded:', animData);
      } catch (err) {
        console.error('Failed to load animation data:', err);
        // Try to load from file_url if direct data endpoint fails
        if (templateData.file_url) {
          try {
            const response = await fetch(templateData.file_url);
            const animData = await response.json();
            setAnimationData(animData);
            console.log('Animation data loaded from file_url:', animData);
          } catch (fileErr) {
            console.error('Failed to load animation data from file_url:', fileErr);
          }
        }
      }
      
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
    if (!promptText.trim() || !template?.id) return;

    try {
      setPromptLoading(true);
      
      // Use the full AI service for natural language processing
      const response = await fetch(`/api/templates/${template.id}/prompt`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          prompt: promptText.trim(),
          state: currentState
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.patches && result.patches.length > 0) {
        // Apply AI-generated patches
        let changesApplied = 0;
        
        for (const patch of result.patches) {
          try {
            await applyPatch(patch);
            changesApplied++;
          } catch (patchError) {
            console.error('Failed to apply patch:', patch, patchError);
          }
        }
        
        // Clear prompt
        setPromptText('');
        
        // Show success message with AI explanation
        alert(`✅ Applied ${changesApplied} changes: ${result.explanation}`);
      } else {
        alert('❌ No changes could be made from your prompt. Try being more specific.');
      }

    } catch (err) {
      console.error('AI prompt processing failed:', err);
      
      // Fallback to simple rule-based processing
      try {
        const prompt = promptText.toLowerCase().trim();
        let changesApplied = 0;
        
        // Handle common prompt commands as fallback
        if (prompt.includes('faster') || prompt.includes('speed')) {
          const speedMatch = prompt.match(/(\d+(?:\.\d+)?)/);
          if (speedMatch) {
            const newSpeed = parseFloat(speedMatch[1]);
            if (newSpeed > 0 && newSpeed <= 5) {
              setSpeed(newSpeed);
              setCurrentState(prev => ({ ...prev, speed: newSpeed }));
              setEditorState(prev => ({
                ...prev,
                canvas: {
                  ...prev.canvas,
                  global_playback_speed: newSpeed
                }
              }));
              changesApplied++;
            }
          }
        }
        
        if (prompt.includes('slower')) {
          const speedMatch = prompt.match(/(\d+(?:\.\d+)?)/);
          if (speedMatch) {
            const newSpeed = parseFloat(speedMatch[1]);
            if (newSpeed > 0 && newSpeed <= 5) {
              setSpeed(newSpeed);
              setCurrentState(prev => ({ ...prev, speed: newSpeed }));
              setEditorState(prev => ({
                ...prev,
                canvas: {
                  ...prev.canvas,
                  global_playback_speed: newSpeed
                }
              }));
              changesApplied++;
            }
          }
        }
        
        if (prompt.includes('color') || prompt.includes('colour')) {
          const colorMatch = prompt.match(/#([0-9a-fA-F]{6})/);
          if (colorMatch) {
            const color = '#' + colorMatch[1];
            // Apply color to first available element
            const elements = template?.editable_parameters_schema?.elements || template?.manifest?.elements || [];
            if (elements.length > 0) {
              const firstElement = elements[0];
              handlePropertyChange(firstElement.id, 'color', color);
              changesApplied++;
            }
          }
        }
        
        if (prompt.includes('background')) {
          const colorMatch = prompt.match(/#([0-9a-fA-F]{6})/);
          if (colorMatch) {
            const color = '#' + colorMatch[1];
            handleCanvasChange('background_color', color);
            changesApplied++;
          }
        }
        
        // Clear prompt
        setPromptText('');
        
        if (changesApplied > 0) {
          alert(`Applied ${changesApplied} changes from prompt (fallback mode)`);
        } else {
          alert('❌ Failed to process prompt. Try: "make it faster", "change color to #FF0000", "set background to #000000"');
        }
      } catch (fallbackError) {
        console.error('Fallback prompt processing failed:', fallbackError);
        alert('❌ Failed to process prompt. Please try again.');
      }
    } finally {
      setPromptLoading(false);
    }
  };

  // Apply AI-generated patches to the animation
  const applyPatch = async (patch) => {
    const { op, path, value } = patch;
    
    if (op === 'replace') {
      // Parse the path to determine what to update
      const pathParts = path.split('/').filter(p => p);
      
      if (pathParts[0] === 'elements' && pathParts.length >= 3) {
        const elementId = pathParts[1];
        const property = pathParts[2];
        
        // Update element property
        handlePropertyChange(elementId, property, value);
        
      } else if (pathParts[0] === 'canvas' && pathParts.length >= 2) {
        const property = pathParts[1];
        
        // Update canvas property
        handleCanvasChange(property, value);
      }
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

  const handlePropertyChange = async (elementId, property, value) => {
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
    
    // Also update currentState for AI processing
    setCurrentState(prev => ({
      ...prev,
      [`elements.${elementId}.${property}`]: value
    }));
    
    // Apply changes to animation data based on property type
    if (animationData) {
      const updatedAnim = JSON.parse(JSON.stringify(animationData));
      
      // Handle different types of property changes
      if (property.includes('color')) {
        // Use bulletproof color changing
        try {
          // Send to backend for bulletproof color change
          const response = await fetch('/api/bulletproof/change-color', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              animation_data: updatedAnim,
              target_color: value,
              color_type: property.includes('stroke') ? 'stroke' : 
                         property.includes('background') ? 'background' : 'fill'
            })
          });
          
          if (response.ok) {
            const result = await response.json();
            setAnimationData(result.animation_data);
            return; // Exit early if backend processing succeeded
          }
        } catch (error) {
          console.warn('Backend color change failed, using frontend fallback:', error);
        }
        
        // Frontend fallback - enhanced color changing
        const layers = updatedAnim.layers || [];
        for (const layer of layers) {
          const shapes = layer.shapes || [];
          for (const shape of shapes) {
            if (shape.ty === 'fl' && shape.c && shape.c.k) { // Fill color
              if (value.startsWith('#')) {
                const hex = value.slice(1);
                const r = parseInt(hex.substr(0, 2), 16) / 255;
                const g = parseInt(hex.substr(2, 2), 16) / 255;
                const b = parseInt(hex.substr(4, 2), 16) / 255;
                shape.c.k = [r, g, b, 1];
              }
            } else if (shape.ty === 'st' && shape.c && shape.c.k) { // Stroke color
              if (value.startsWith('#')) {
                const hex = value.slice(1);
                const r = parseInt(hex.substr(0, 2), 16) / 255;
                const g = parseInt(hex.substr(2, 2), 16) / 255;
                const b = parseInt(hex.substr(4, 2), 16) / 255;
                shape.c.k = [r, g, b, 1];
              }
            }
          }
        }
      } else if (property === 'scale') {
        // Scale changes
        const layers = updatedAnim.layers || [];
        for (const layer of layers) {
          if (layer.ks && layer.ks.s && layer.ks.s.k) {
            // Scale property
            if (Array.isArray(layer.ks.s.k)) {
              layer.ks.s.k = [value * 100, value * 100, 100]; // Convert to percentage
            } else if (typeof layer.ks.s.k === 'number') {
              layer.ks.s.k = value * 100;
            }
          }
        }
      } else if (property === 'rotation') {
        // Rotation changes
        const layers = updatedAnim.layers || [];
        for (const layer of layers) {
          if (layer.ks && layer.ks.r && layer.ks.r.k) {
            layer.ks.r.k = value;
          }
        }
      } else if (property === 'opacity') {
        // Opacity changes
        const layers = updatedAnim.layers || [];
        for (const layer of layers) {
          if (layer.ks && layer.ks.o && layer.ks.o.k) {
            layer.ks.o.k = value * 100; // Convert to percentage
          }
        }
      } else if (property === 'x' || property === 'y') {
        // Position changes
        const layers = updatedAnim.layers || [];
        for (const layer of layers) {
          if (layer.ks && layer.ks.p && layer.ks.p.k) {
            if (Array.isArray(layer.ks.p.k)) {
              if (property === 'x') {
                layer.ks.p.k[0] = value;
              } else if (property === 'y') {
                layer.ks.p.k[1] = value;
              }
            }
          }
        }
      } else if (property === 'content') {
        // Text content changes
        const layers = updatedAnim.layers || [];
        for (const layer of layers) {
          if (layer.ty === 5) { // Text layer
            const textData = layer.t?.d?.k?.[0]?.s;
            if (textData) {
              textData.t = value;
            }
          }
        }
      } else if (property === 'font_size') {
        // Font size changes
        const layers = updatedAnim.layers || [];
        for (const layer of layers) {
          if (layer.ty === 5) { // Text layer
            const textData = layer.t?.d?.k?.[0]?.s;
            if (textData && textData.s) {
              textData.s.s = value;
            }
          }
        }
      }
      
      setAnimationData(updatedAnim);
    }
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
            animationData={animationData}
            editorState={editorState}
            selectedElements={selectedElements}
            zoom={zoom}
            isPlaying={isPlaying}
            onElementSelect={handleElementSelect}
            onElementTransform={handleElementTransform}
            onCanvasChange={handleCanvasChange}
          />
        </div>
        
        {/* AI Natural Language Editor */}
        <div className="border-t border-gray-200 p-6 bg-gradient-to-r from-orange-50 to-red-50">
          <div className="flex items-center space-x-3 mb-3">
            <div className="flex items-center space-x-2">
              <Zap className="w-6 h-6 text-orange-500" />
              <h3 className="text-lg font-bold text-orange-800">🤖 AI Natural Language Editor</h3>
            </div>
          </div>
          
          <p className="text-sm text-orange-700 mb-4">
            Describe any change you want to make in natural language. The AI will understand and apply it!
          </p>
          
          <div className="flex items-center space-x-3 mb-3">
            <input
              type="text"
              placeholder="Try: 'Move the text to center', 'Make it bigger', 'Change color to blue', 'Rotate 45 degrees', 'Make it transparent'..."
              value={promptText}
              onChange={(e) => setPromptText(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handlePrompt()}
              className="flex-1 px-4 py-3 border-2 border-orange-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500 text-lg"
            />
            <button
              onClick={handlePrompt}
              disabled={!promptText.trim() || promptLoading}
              className="px-6 py-3 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-lg hover:from-orange-600 hover:to-red-600 disabled:opacity-50 font-semibold text-lg shadow-lg"
            >
              {promptLoading ? '🔄 Processing...' : '✨ Apply'}
            </button>
          </div>
          
          <div className="grid grid-cols-2 gap-4 text-xs text-orange-600">
            <div>
              <strong>Position & Size:</strong>
              <ul className="list-disc list-inside space-y-1 mt-1">
                <li>"Move to center"</li>
                <li>"Make it bigger"</li>
                <li>"Position at top left"</li>
                <li>"Scale to 150%"</li>
              </ul>
            </div>
            <div>
              <strong>Colors & Effects:</strong>
              <ul className="list-disc list-inside space-y-1 mt-1">
                <li>"Change to blue"</li>
                <li>"Make it transparent"</li>
                <li>"Set background to white"</li>
                <li>"Add red border"</li>
              </ul>
            </div>
            <div>
              <strong>Animation & Text:</strong>
              <ul className="list-disc list-inside space-y-1 mt-1">
                <li>"Make it faster"</li>
                <li>"Change text to 'Hello'"</li>
                <li>"Rotate 90 degrees"</li>
                <li>"Increase font size"</li>
              </ul>
            </div>
            <div>
              <strong>Shapes & Forms:</strong>
              <ul className="list-disc list-inside space-y-1 mt-1">
                <li>"Make it round"</li>
                <li>"Change to square"</li>
                <li>"Add rounded corners"</li>
                <li>"Make it invisible"</li>
              </ul>
            </div>
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