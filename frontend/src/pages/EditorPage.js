import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { Play, Pause, RotateCcw, Save, Settings, Palette, Type, Image, Zap } from 'lucide-react';
import { apiService } from '../services/api';

// Import dotLottie player dynamically
const DotLottiePlayer = React.lazy(() => 
  import('@dotlottie/player-component').then(module => ({
    default: React.forwardRef((props, ref) => {
      useEffect(() => {
        // Register the web component if not already registered
        if (!customElements.get('dotlottie-player')) {
          import('@dotlottie/player-component');
        }
      }, []);

      // Use React.createElement to create the web component
      return React.createElement('dotlottie-player', {
        ...props,
        ref,
        autoplay: false,
        loop: true,
        controls: false,
        mode: 'normal',
        style: {
          width: '100%',
          height: '100%',
          ...props.style
        }
      });
    })
  }))
);

const EditorPage = () => {
  const { templateId } = useParams();
  const playerRef = useRef(null);
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

  // Load template data
  useEffect(() => {
    loadTemplate();
  }, [templateId]);

  // Initialize player when animation data is available
  useEffect(() => {
    if (animationData && playerRef.current) {
      initializePlayer();
    }
  }, [animationData]);

  const loadTemplate = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load template metadata
      const templateData = await apiService.get(`/templates/${templateId}`);
      setTemplate(templateData);

      // Load animation data
      const animData = await apiService.get(`/templates/${templateId}/data`);
      setAnimationData(animData);

      // Load saved revisions
      try {
        const revisions = await apiService.get(`/templates/${templateId}/revisions?user_id=current_user`);
        if (revisions.length > 0) {
          setCurrentState(revisions[0].state);
        }
      } catch (revisionError) {
        console.log('No previous revisions found');
      }

    } catch (err) {
      console.error('Failed to load template:', err);
      setError('Failed to load template. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const initializePlayer = () => {
    const player = playerRef.current;
    if (!player || !animationData) return;

    try {
      console.log('Initializing player with animation data:', Object.keys(animationData));
      
      // For dotLottie player, we need to pass the JSON data directly
      // The player.load() method accepts JSON data
      player.load(JSON.stringify(animationData));
      
      // Set initial playback settings
      player.setSpeed(speed);
      player.setLoop(true);
      
      // Set up event listeners
      player.addEventListener('ready', () => {
        console.log('Player ready, starting playback');
        player.play();
        applyCurrentState();
      });

      player.addEventListener('play', () => {
        console.log('Player started');
        setIsPlaying(true);
      });
      
      player.addEventListener('pause', () => {
        console.log('Player paused');
        setIsPlaying(false);
      });

      player.addEventListener('error', (e) => {
        console.error('Player error:', e);
        setError('Failed to load animation');
      });

    } catch (err) {
      console.error('Failed to initialize player:', err);
      setError('Failed to initialize animation player');
    }
  };

  const applyCurrentState = () => {
    if (!playerRef.current || !currentState || Object.keys(currentState).length === 0) return;

    try {
      // Apply speed changes
      if (currentState.speed !== undefined) {
        setSpeed(currentState.speed);
        playerRef.current.setSpeed(currentState.speed);
      }

      // Apply other state changes would go here
      // This is a simplified version - full implementation would apply
      // text changes, color changes, etc. to the animation data

    } catch (err) {
      console.error('Failed to apply state:', err);
    }
  };

  const handlePlay = () => {
    if (playerRef.current) {
      if (isPlaying) {
        playerRef.current.pause();
      } else {
        playerRef.current.play();
      }
    }
  };

  const handleSpeedChange = (newSpeed) => {
    setSpeed(newSpeed);
    setCurrentState(prev => ({ ...prev, speed: newSpeed }));
    
    if (playerRef.current) {
      playerRef.current.setSpeed(newSpeed);
    }
  };

  const handleReset = () => {
    if (playerRef.current) {
      playerRef.current.seek(0);
      playerRef.current.play();
    }
  };

  const handleSave = async () => {
    try {
      await apiService.post(`/templates/${templateId}/revisions`, {
        template_id: templateId,
        user_id: 'current_user',
        state: currentState
      });
      
      // Show success feedback
      const saveBtn = document.querySelector('[data-save-btn]');
      if (saveBtn) {
        saveBtn.textContent = 'Saved!';
        setTimeout(() => saveBtn.textContent = 'Save', 1000);
      }
    } catch (err) {
      console.error('Failed to save:', err);
      alert('Failed to save changes');
    }
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
            // Apply patch to state
            const pathParts = patch.path.split('/').filter(p => p);
            if (pathParts.length > 0) {
              newState[pathParts.join('.')] = patch.value;
            }
          }
        });
        
        setCurrentState(newState);
        applyCurrentState();
        
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

  const handleTextChange = (elementId, newText) => {
    setCurrentState(prev => ({
      ...prev,
      [`text.${elementId}`]: newText
    }));
    
    // In a full implementation, this would update the animation data
    // and refresh the player
  };

  const handleColorChange = (elementId, newColor) => {
    setCurrentState(prev => ({
      ...prev,
      [`colors.${elementId}`]: newColor
    }));
    
    // In a full implementation, this would update the animation data
    // and refresh the player
  };

  const handleImageChange = (elementId, newImageUrl) => {
    setCurrentState(prev => ({
      ...prev,
      [`images.${elementId}`]: newImageUrl
    }));
    
    // In a full implementation, this would update the animation data
    // and refresh the player
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
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Template Load Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={loadTemplate}
            className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="flex h-screen">
        
        {/* Left Panel - Player */}
        <div className="flex-1 flex flex-col bg-white">
          
          {/* Top Controls */}
          <div className="border-b border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <h1 className="text-xl font-semibold text-gray-900">
                  {template?.name || 'Template Editor'}
                </h1>
                
                <div className="flex items-center space-x-2">
                  <button
                    onClick={handlePlay}
                    className="p-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600"
                  >
                    {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
                  </button>
                  
                  <button
                    onClick={handleReset}
                    className="p-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                  >
                    <RotateCcw className="w-5 h-5" />
                  </button>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <button
                  onClick={handleSave}
                  data-save-btn
                  className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 flex items-center"
                >
                  <Save className="w-4 h-4 mr-2" />
                  Save
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
          
          {/* Player Area */}
          <div className="flex-1 flex items-center justify-center p-8 bg-gray-100">
            <div className="relative bg-white rounded-lg shadow-lg overflow-hidden">
              <React.Suspense fallback={<div className="w-96 h-96 bg-gray-200 animate-pulse"></div>}>
                <DotLottiePlayer
                  ref={playerRef}
                  style={{
                    width: '400px',
                    height: '400px'
                  }}
                  loop
                  controls={false}
                />
              </React.Suspense>
            </div>
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
        
        {/* Right Panel - Inspector */}
        <div className="w-80 bg-white border-l border-gray-200 flex flex-col">
          
          {/* Inspector Header */}
          <div className="border-b border-gray-200 p-4">
            <h2 className="text-lg font-semibold text-gray-900">Inspector</h2>
          </div>
          
          {/* Inspector Content */}
          <div className="flex-1 overflow-y-auto p-4 space-y-6">
            
            {/* Text Elements */}
            {template?.manifest?.text && template.manifest.text.length > 0 && (
              <div>
                <div className="flex items-center mb-3">
                  <Type className="w-5 h-5 text-gray-600 mr-2" />
                  <h3 className="font-medium text-gray-900">Text</h3>
                </div>
                
                <div className="space-y-3">
                  {template.manifest.text.map((textElement) => (
                    <div key={textElement.id}>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {textElement.label}
                      </label>
                      <input
                        type="text"
                        defaultValue={textElement.default || ''}
                        onChange={(e) => handleTextChange(textElement.id, e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500/20"
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Color Elements */}
            {template?.manifest?.colors && template.manifest.colors.length > 0 && (
              <div>
                <div className="flex items-center mb-3">
                  <Palette className="w-5 h-5 text-gray-600 mr-2" />
                  <h3 className="font-medium text-gray-900">Colors</h3>
                </div>
                
                <div className="space-y-3">
                  {template.manifest.colors.map((colorElement) => (
                    <div key={colorElement.id}>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {colorElement.label}
                      </label>
                      <div className="flex items-center space-x-2">
                        <input
                          type="color"
                          defaultValue={colorElement.default || '#000000'}
                          onChange={(e) => handleColorChange(colorElement.id, e.target.value)}
                          className="w-12 h-8 border border-gray-300 rounded cursor-pointer"
                        />
                        <input
                          type="text"
                          defaultValue={colorElement.default || '#000000'}
                          onChange={(e) => handleColorChange(colorElement.id, e.target.value)}
                          className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500/20 font-mono text-sm"
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Image Elements */}
            {template?.manifest?.images && template.manifest.images.length > 0 && (
              <div>
                <div className="flex items-center mb-3">
                  <Image className="w-5 h-5 text-gray-600 mr-2" />
                  <h3 className="font-medium text-gray-900">Images</h3>
                </div>
                
                <div className="space-y-3">
                  {template.manifest.images.map((imageElement) => (
                    <div key={imageElement.id}>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {imageElement.label}
                      </label>
                      <input
                        type="url"
                        placeholder="https://example.com/image.jpg"
                        onChange={(e) => handleImageChange(imageElement.id, e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500/20"
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}
            
          </div>
        </div>
        
      </div>
      
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
              <h4 className="font-medium text-gray-700">Current State:</h4>
              <pre className="text-gray-600 bg-gray-50 p-2 rounded overflow-x-auto">
                {JSON.stringify(currentState, null, 2)}
              </pre>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-700">Manifest:</h4>
              <pre className="text-gray-600 bg-gray-50 p-2 rounded overflow-x-auto">
                {JSON.stringify(template?.manifest || {}, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      )}
      
    </div>
  );
};

export default EditorPage;