import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { Play, Pause, RotateCcw, Save, Settings, Palette, Type, Image, Zap, Download, Crown } from 'lucide-react';
import { apiService } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import LottieRenderer from '../components/editor/LottieRenderer';
import SubscriptionModal from '../components/subscription/SubscriptionModal';
import ExportModal from '../components/editor/ExportModal';

const EditorPage = () => {
  const { templateId } = useParams();
  const [template, setTemplate] = useState(null);
  const [animationData, setAnimationData] = useState(null);
  const [currentState, setCurrentState] = useState({});
  const [isPlaying, setIsPlaying] = useState(false);
  const [speed, setSpeed] = useState(1.0);
  const [canvasSize, setCanvasSize] = useState({ width: 400, height: 400 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showDebug, setShowDebug] = useState(false);
  const [promptText, setPromptText] = useState('');
  const [promptLoading, setPromptLoading] = useState(false);
  const [showSubscription, setShowSubscription] = useState(false);
  const [showExportModal, setShowExportModal] = useState(false);
  const [exportLoading, setExportLoading] = useState(false);
  
  const { user } = useAuth();

  // Load template data
  useEffect(() => {
    loadTemplate();
  }, [templateId]);

  const loadTemplate = async () => {
    try {
      setLoading(true);
      setError(null);

      console.log('Loading template:', templateId);

      // Load template metadata
      const templateData = await apiService.get(`/templates/${templateId}`);
      console.log('Template data loaded:', templateData);
      setTemplate(templateData);

      // Load animation data
      const animData = await apiService.get(`/templates/${templateId}/data`);
      console.log('Animation data loaded:', animData);
      setAnimationData(animData);

      // Load saved revisions
      try {
        const revisions = await apiService.getRevisions(templateId);
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

  const handleSave = async () => {
    try {
      await apiService.post(`/templates/${templateId}/revisions`, {
        template_id: templateId,
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

  const handleExport = async (format, resolution) => {
    if (!user) {
      setShowSubscription(true);
      return;
    }

    // Check if user has credits
    if (user.credits_remaining <= 0) {
      setShowSubscription(true);
      return;
    }

    setExportLoading(true);
    
    try {
      const result = await apiService.createExport(
        templateId,
        currentState,
        format,
        resolution
      );
      
      // Show success and download link
      alert(`Export successful! Download: ${result.download_url}`);
      
      // Refresh user data to update credits
      window.location.reload();
      
    } catch (error) {
      if (error.response?.status === 402) {
        setShowSubscription(true);
      } else {
        alert('Export failed: ' + (error.response?.data?.detail || error.message));
      }
    } finally {
      setExportLoading(false);
      setShowExportModal(false);
    }
  };

  const setBySelector = (obj, selector, value) => {
    // Supports selectors like: layers[0].t.d.k[0].s.t
    try {
      const tokens = selector.replace(/\]/g, '').split(/\.|\[/).filter(Boolean);
      let cursor = obj;
      for (let i = 0; i < tokens.length - 1; i++) {
        const key = isNaN(+tokens[i]) ? tokens[i] : +tokens[i];
        if (cursor[key] === undefined) return false;
        cursor = cursor[key];
      }
      const last = tokens[tokens.length - 1];
      const lastKey = isNaN(+last) ? last : +last;
      cursor[lastKey] = value;
      return true;
    } catch (e) {
      console.warn('setBySelector failed', selector, e);
      return false;
    }
  };

  const hexToRgbaArray = (hex) => {
    const m = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    if (!m) return [1, 1, 1, 1];
    const r = parseInt(m[1], 16) / 255;
    const g = parseInt(m[2], 16) / 255;
    const b = parseInt(m[3], 16) / 255;
    return [r, g, b, 1];
  };

  const applyPatchesToAnimation = (patches, manifest, anim) => {
    if (!patches || patches.length === 0 || !anim) return anim;
    const updated = JSON.parse(JSON.stringify(anim));

    for (const patch of patches) {
      const { op, path, value } = patch;
      if (op !== 'replace') continue;

      // Speed
      if (path === '/speed') {
        setSpeed(typeof value === 'number' ? value : 1.0);
        continue;
      }

      // Text
      if (path.startsWith('/text/')) {
        const id = path.split('/')[2];
        const t = (manifest?.text || []).find(x => x.id === id);
        if (t?.selector) setBySelector(updated, t.selector, value);
        continue;
      }

      // Colors
      if (path.startsWith('/colors/')) {
        const id = path.split('/')[2];
        const c = (manifest?.colors || []).find(x => x.id === id);
        if (c?.selector) setBySelector(updated, c.selector, hexToRgbaArray(value));
        continue;
      }

      // Images
      if (path.startsWith('/images/')) {
        const id = path.split('/')[2];
        const img = (manifest?.images || []).find(x => x.id === id);
        const assetId = img?.asset_id;
        if (assetId && Array.isArray(updated.assets)) {
          const asset = updated.assets.find(a => a.id === assetId);
          if (asset) {
            asset.u = '';
            asset.p = value;
          }
        }
        continue;
      }

      // Font family
      if (path === '/font/family') {
        const family = String(value || '').trim();
        if (updated.fonts?.list && Array.isArray(updated.fonts.list)) {
          if (!updated.fonts.list.find(f => f.fFamily === family || f.fName === family)) {
            updated.fonts.list.push({ fName: family, fFamily: family, fStyle: 'Regular', ascent: 75 });
          }
        }
        (manifest?.text || []).forEach(t => {
          const sel = t.selector?.replace(/\.t$/, '.f');
          if (sel) setBySelector(updated, sel, family);
        });
        continue;
      }

      // Font size
      if (path === '/font/size') {
        const size = Number(value) || 24;
        (manifest?.text || []).forEach(t => {
          const sel = t.selector?.replace(/\.t$/, '.s.s');
          if (sel) setBySelector(updated, sel, size);
        });
        continue;
      }

      // Canvas aspect ratio handled in caller by setCanvasSize
      if (path === '/canvas/aspect') {
        const preset = (value || '').toString().toLowerCase();
        if (preset.includes('16:9') || preset.includes('youtube') || preset.includes('widescreen')) {
          setCanvasSize({ width: 1280, height: 720 });
        } else if (preset.includes('9:16') || preset.includes('vertical') || preset.includes('tiktok') || preset.includes('story') || preset.includes('reel')) {
          setCanvasSize({ width: 720, height: 1280 });
        } else if (preset.includes('1:1') || preset.includes('square') || preset.includes('instagram post')) {
          setCanvasSize({ width: 1080, height: 1080 });
        }
        continue;
      }

      // Transforms
      if (path === '/transform/op' && value && typeof value === 'object') {
        const { type, factor, degrees, dx, dy, targetLabel } = value;
        // Affect matching text layers by label; fallback to first text layer
        const targets = (manifest?.text || []).filter(t => !targetLabel || (t.label || '').toLowerCase().includes(targetLabel));
        const targetList = targets.length > 0 ? targets : (manifest?.text || []).slice(0, 1);
        targetList.forEach(t => {
          // Map text selector to the layer index to modify transform keys
          const m = /layers\[(\d+)\]/.exec(t.selector || '');
          if (!m) return;
          const li = parseInt(m[1], 10);
          const layer = updated.layers?.[li];
          if (!layer) return;
          const ks = layer.ks || (layer.ks = {});
          // Position
          if (type === 'translate' && (dx || dy)) {
            const p = ks.p || (ks.p = { a: 0, k: [layer.ks?.p?.k?.[0] || 0, layer.ks?.p?.k?.[1] || 0, 0] });
            const k = Array.isArray(p.k) ? p.k : [0, 0, 0];
            p.k = [k[0] + (dx || 0), k[1] + (dy || 0), 0];
          }
          // Scale (percentage)
          if (type === 'scale' && factor) {
            const s = ks.s || (ks.s = { a: 0, k: [100, 100, 100] });
            s.k = [Math.round(s.k[0] * factor), Math.round(s.k[1] * factor), 100];
          }
          // Rotation
          if (type === 'rotate' && typeof degrees === 'number') {
            const r = ks.r || (ks.r = { a: 0, k: 0 });
            r.k = (r.k || 0) + degrees;
          }
        });
        continue;
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

  const handleTextChange = (elementId, newText) => {
    setCurrentState(prev => ({
      ...prev,
      [`text.${elementId}`]: newText
    }));
  };

  const handleColorChange = (elementId, newColor) => {
    setCurrentState(prev => ({
      ...prev,
      [`colors.${elementId}`]: newColor
    }));
  };

  const handleImageChange = (elementId, newImageUrl) => {
    setCurrentState(prev => ({
      ...prev,
      [`images.${elementId}`]: newImageUrl
    }));
  };

  const handleSpeedChange = (newSpeed) => {
    setSpeed(newSpeed);
    setCurrentState(prev => ({ ...prev, speed: newSpeed }));
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
                  {template?.title || 'Template Editor'}
                </h1>
                
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setIsPlaying(!isPlaying)}
                    className="p-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600"
                  >
                    {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
                  </button>
                  
                  <button
                    onClick={() => console.log('Reset clicked')}
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
          
          {/* Player Area */}
          <div className="flex-1 flex items-center justify-center p-8 bg-gray-100">
            <div className="relative bg-white rounded-lg shadow-lg overflow-hidden flex items-center justify-center" style={{width: `${canvasSize.width}px`, height: `${canvasSize.height}px`}}>
              {animationData ? (
                <LottieRenderer
                  animationData={animationData}
                  isPlaying={isPlaying}
                  speed={speed}
                  loop={true}
                  autoplay={true}
                  className="w-full h-full"
                />
              ) : (
                <div className="w-full h-full bg-gray-200 flex items-center justify-center">
                  <div className="text-gray-500">No animation loaded</div>
                </div>
              )}
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
                  {template.manifest.colors.slice(0, 5).map((colorElement) => (
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
                  {template.manifest.colors.length > 5 && (
                    <div className="text-sm text-gray-500 text-center py-2">
                      ... and {template.manifest.colors.length - 5} more colors
                    </div>
                  )}
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
      
      {/* Export Modal */}
      <ExportModal
        isOpen={showExportModal}
        onClose={() => setShowExportModal(false)}
        onExport={handleExport}
        loading={exportLoading}
      />

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