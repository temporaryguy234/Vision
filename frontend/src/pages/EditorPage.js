import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  Save, 
  RotateCcw, 
  RotateCw, 
  ZoomIn,
  ZoomOut,
  Play,
  Pause,
  Copy,
  Trash2,
  AlignLeft,
  AlignCenter,
  AlignRight,
  AlignHorizontalJustifyCenter,
  AlignVerticalJustifyCenter
} from 'lucide-react';
import { apiService } from '../services/api';
import Canvas from '../components/editor/Canvas';
import PropertiesPanel from '../components/editor/PropertiesPanel';
import ElementTransformer from '../components/editor/ElementTransformer';
import HistoryManager from '../utils/HistoryManager';

const EditorPage = () => {
  const { templateId } = useParams();
  const navigate = useNavigate();
  const canvasRef = useRef(null);
  
  // Core state
  const [template, setTemplate] = useState(null);
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  
  // Editor state
  const [editorState, setEditorState] = useState({
    canvas: {},
    elements: {}
  });
  const [selectedElements, setSelectedElements] = useState([]);
  const [activeTab, setActiveTab] = useState('Content');
  const [zoom, setZoom] = useState(100);
  const [isPlaying, setIsPlaying] = useState(false);
  const [commandInput, setCommandInput] = useState('');
  
  // History system
  const [historyManager] = useState(() => new HistoryManager());
  const [canUndo, setCanUndo] = useState(false);
  const [canRedo, setCanRedo] = useState(false);
  
  // Brand kits
  const [brandKits, setBrandKits] = useState([]);
  const [activeBrandKit, setActiveBrandKit] = useState(null);
  
  // Load template and create/load project
  useEffect(() => {
    const loadEditor = async () => {
      if (!templateId) return;
      
      try {
        setLoading(true);
        
        // Load template
        const templateData = await apiService.getTemplate(templateId);
        setTemplate(templateData);
        
        // Try to find existing project or create new one
        const existingProjects = await apiService.getProjects('current_user', { template_id: templateId });
        let projectData;
        
        if (existingProjects.length > 0) {
          // Use existing project
          projectData = existingProjects[0];
        } else {
          // Create new project
          projectData = await apiService.createProject({
            template_id: templateId,
            title: `Project from ${templateData.title}`,
            user_id: 'current_user'
          });
        }
        
        setProject(projectData);
        setEditorState(projectData.current_editor_state || {
          canvas: templateData.editable_parameters_schema.canvas,
          elements: {}
        });
        
        // Initialize history
        historyManager.initialize(projectData.current_editor_state);
        updateHistoryButtons();
        
        // Load brand kits
        const userBrandKits = await apiService.getBrandKits('current_user');
        setBrandKits(userBrandKits);
        
      } catch (err) {
        console.error('Error loading editor:', err);
        setError('Failed to load template');
      } finally {
        setLoading(false);
      }
    };
    
    loadEditor();
  }, [templateId]);
  
  // Update history buttons
  const updateHistoryButtons = useCallback(() => {
    setCanUndo(historyManager.canUndo());
    setCanRedo(historyManager.canRedo());
  }, [historyManager]);
  
  // Handle element selection
  const handleElementSelect = useCallback((elementId, multiSelect = false) => {
    if (multiSelect) {
      setSelectedElements(prev => 
        prev.includes(elementId) 
          ? prev.filter(id => id !== elementId)
          : [...prev, elementId]
      );
    } else {
      setSelectedElements([elementId]);
    }
  }, []);
  
  // Handle element transformation
  const handleElementTransform = useCallback((elementId, transform) => {
    const oldState = { ...editorState };
    const newState = {
      ...editorState,
      elements: {
        ...editorState.elements,
        [elementId]: {
          ...editorState.elements[elementId],
          ...transform
        }
      }
    };
    
    // Add to history
    historyManager.addAction({
      type: 'transform',
      elementId,
      oldState,
      newState,
      timestamp: Date.now()
    });
    
    setEditorState(newState);
    updateHistoryButtons();
  }, [editorState, historyManager, updateHistoryButtons]);
  
  // Handle property change
  const handlePropertyChange = useCallback((elementId, property, value, oldValue) => {
    // Validate the change based on template schema
    const element = template?.editable_parameters_schema.elements.find(e => e.id === elementId);
    if (!element) return;
    
    // TODO: Add comprehensive validation based on element type and property
    
    const oldState = { ...editorState };
    const newState = {
      ...editorState,
      elements: {
        ...editorState.elements,
        [elementId]: {
          ...editorState.elements[elementId],
          [property]: value
        }
      }
    };
    
    // Add to history
    historyManager.addAction({
      type: 'property',
      elementId,
      property,
      oldValue,
      newValue: value,
      oldState,
      newState,
      timestamp: Date.now()
    });
    
    setEditorState(newState);
    updateHistoryButtons();
  }, [editorState, template, historyManager, updateHistoryButtons]);
  
  // Handle canvas property change
  const handleCanvasChange = useCallback((property, value, oldValue) => {
    const oldState = { ...editorState };
    const newState = {
      ...editorState,
      canvas: {
        ...editorState.canvas,
        [property]: value
      }
    };
    
    historyManager.addAction({
      type: 'canvas',
      property,
      oldValue,
      newValue: value,
      oldState,
      newState,
      timestamp: Date.now()
    });
    
    setEditorState(newState);
    updateHistoryButtons();
  }, [editorState, historyManager, updateHistoryButtons]);
  
  // Undo/Redo
  const handleUndo = useCallback(() => {
    const previousState = historyManager.undo();
    if (previousState) {
      setEditorState(previousState);
      updateHistoryButtons();
    }
  }, [historyManager, updateHistoryButtons]);
  
  const handleRedo = useCallback(() => {
    const nextState = historyManager.redo();
    if (nextState) {
      setEditorState(nextState);
      updateHistoryButtons();
    }
  }, [historyManager, updateHistoryButtons]);
  
  // Save project
  const handleSave = useCallback(async () => {
    if (!project) return;
    
    try {
      setSaving(true);
      await apiService.updateProject(project.id, {
        current_editor_state: editorState,
        updated_at: new Date().toISOString()
      });
      
      // Show success feedback
      // TODO: Add toast notification system
      console.log('Project saved successfully');
      
    } catch (err) {
      console.error('Error saving project:', err);
      setError('Failed to save project');
    } finally {
      setSaving(false);
    }
  }, [project, editorState]);
  
  // Save as new project
  const handleSaveAs = useCallback(async () => {
    if (!template) return;
    
    const title = prompt('Enter project name:', `Copy of ${project?.title || template.title}`);
    if (!title) return;
    
    try {
      setSaving(true);
      const newProject = await apiService.createProject({
        template_id: templateId,
        title,
        user_id: 'current_user'
      });
      
      await apiService.updateProject(newProject.id, {
        current_editor_state: editorState
      });
      
      setProject(newProject);
      console.log('Project saved as new project');
      
    } catch (err) {
      console.error('Error saving as new project:', err);
      setError('Failed to save as new project');
    } finally {
      setSaving(false);
    }
  }, [template, project, templateId, editorState]);
  
  // Handle alignment
  const handleAlign = useCallback((alignment) => {
    if (selectedElements.length === 0) return;
    
    const oldState = { ...editorState };
    let newElements = { ...editorState.elements };
    
    selectedElements.forEach(elementId => {
      const element = newElements[elementId] || {};
      
      switch (alignment) {
        case 'left':
          newElements[elementId] = { ...element, x: 0 };
          break;
        case 'center-h':
          newElements[elementId] = { ...element, x: 50 };
          break;
        case 'right':
          newElements[elementId] = { ...element, x: 100 };
          break;
        case 'top':
          newElements[elementId] = { ...element, y: 0 };
          break;
        case 'center-v':
          newElements[elementId] = { ...element, y: 50 };
          break;
        case 'bottom':
          newElements[elementId] = { ...element, y: 100 };
          break;
      }
    });
    
    const newState = { ...editorState, elements: newElements };
    
    historyManager.addAction({
      type: 'align',
      alignment,
      elements: selectedElements,
      oldState,
      newState,
      timestamp: Date.now()
    });
    
    setEditorState(newState);
    updateHistoryButtons();
  }, [selectedElements, editorState, historyManager, updateHistoryButtons]);
  
  // Apply brand kit
  const handleApplyBrandKit = useCallback((brandKit) => {
    if (!brandKit || selectedElements.length === 0) return;
    
    const oldState = { ...editorState };
    let newElements = { ...editorState.elements };
    
    selectedElements.forEach(elementId => {
      const element = newElements[elementId] || {};
      const templateElement = template?.editable_parameters_schema.elements.find(e => e.id === elementId);
      
      if (templateElement?.type === 'text' && brandKit.colors.length > 0) {
        newElements[elementId] = { 
          ...element, 
          color: brandKit.colors[0],
          font_family: brandKit.fonts[0] || element.font_family
        };
      }
    });
    
    const newState = { ...editorState, elements: newElements };
    
    historyManager.addAction({
      type: 'brand-kit',
      brandKitId: brandKit.id,
      elements: selectedElements,
      oldState,
      newState,
      timestamp: Date.now()
    });
    
    setEditorState(newState);
    setActiveBrandKit(brandKit);
    updateHistoryButtons();
  }, [selectedElements, editorState, template, historyManager, updateHistoryButtons]);
  
  // Handle zoom
  const handleZoom = useCallback((direction) => {
    setZoom(prev => {
      const newZoom = direction === 'in' 
        ? Math.min(200, prev + 25) 
        : Math.max(25, prev - 25);
      return newZoom;
    });
  }, []);
  
  // Handle command input (placeholder for now)
  const handleCommandSubmit = useCallback(() => {
    // TODO: Implement natural language command processing
    console.log('Command:', commandInput);
    setCommandInput('');
  }, [commandInput]);
  
  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-orange-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading template...</p>
        </div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button 
            onClick={() => navigate('/templates')}
            className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600"
          >
            Back to Templates
          </button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Top Bar */}
      <div className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/templates')}
            className="flex items-center px-3 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            <span className="hidden sm:inline">Templates</span>
          </button>
          
          <div className="text-sm text-gray-500">
            <span className="font-medium text-gray-900">{template?.title}</span>
            {project && <span> • {project.title}</span>}
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          {/* History Controls */}
          <button
            onClick={handleUndo}
            disabled={!canUndo}
            className="p-2 text-gray-600 hover:text-gray-900 disabled:text-gray-400 disabled:cursor-not-allowed rounded-lg hover:bg-gray-100 transition-colors"
            title="Undo"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
          
          <button
            onClick={handleRedo}
            disabled={!canRedo}
            className="p-2 text-gray-600 hover:text-gray-900 disabled:text-gray-400 disabled:cursor-not-allowed rounded-lg hover:bg-gray-100 transition-colors"
            title="Redo"
          >
            <RotateCw className="w-4 h-4" />
          </button>
          
          <div className="w-px h-6 bg-gray-300 mx-2"></div>
          
          {/* Zoom Controls */}
          <button
            onClick={() => handleZoom('out')}
            disabled={zoom <= 25}
            className="p-2 text-gray-600 hover:text-gray-900 disabled:text-gray-400 disabled:cursor-not-allowed rounded-lg hover:bg-gray-100 transition-colors"
            title="Zoom Out"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          
          <span className="text-sm text-gray-600 min-w-[3rem] text-center">{zoom}%</span>
          
          <button
            onClick={() => handleZoom('in')}
            disabled={zoom >= 200}
            className="p-2 text-gray-600 hover:text-gray-900 disabled:text-gray-400 disabled:cursor-not-allowed rounded-lg hover:bg-gray-100 transition-colors"
            title="Zoom In"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          
          <div className="w-px h-6 bg-gray-300 mx-2"></div>
          
          {/* Playback Controls */}
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="p-2 text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-100 transition-colors"
            title={isPlaying ? 'Pause' : 'Play'}
          >
            {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
          </button>
          
          <div className="w-px h-6 bg-gray-300 mx-2"></div>
          
          {/* Save Controls */}
          <button
            onClick={handleSave}
            disabled={saving}
            className="flex items-center px-3 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 disabled:bg-gray-400 transition-colors"
          >
            <Save className="w-4 h-4 mr-2" />
            <span className="hidden sm:inline">{saving ? 'Saving...' : 'Save'}</span>
          </button>
          
          <button
            onClick={handleSaveAs}
            disabled={saving}
            className="hidden sm:flex items-center px-3 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:bg-gray-100 transition-colors"
          >
            Save As...
          </button>
        </div>
      </div>
      
      {/* Command Input Bar (Mobile) */}
      <div className="md:hidden bg-white border-b border-gray-200 px-4 py-3">
        <div className="flex items-center space-x-2">
          <input
            type="text"
            placeholder="Type a command..."
            value={commandInput}
            onChange={(e) => setCommandInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleCommandSubmit()}
            className="flex-1 px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-300"
          />
          <button
            onClick={handleCommandSubmit}
            className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors"
          >
            Run
          </button>
        </div>
      </div>
      
      {/* Main Editor Area */}
      <div className="flex-1 flex flex-col md:flex-row overflow-hidden">
        {/* Canvas Area */}
        <div className="flex-1 flex flex-col bg-gray-100">
          {/* Alignment Tools */}
          {selectedElements.length > 0 && (
            <div className="bg-white border-b border-gray-200 px-4 py-2 flex items-center space-x-2 text-sm">
              <span className="text-gray-600 mr-2">Align:</span>
              
              <button
                onClick={() => handleAlign('left')}
                className="p-1 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded"
                title="Align Left"
              >
                <AlignLeft className="w-4 h-4" />
              </button>
              
              <button
                onClick={() => handleAlign('center-h')}
                className="p-1 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded"
                title="Center Horizontally"
              >
                <AlignCenter className="w-4 h-4" />
              </button>
              
              <button
                onClick={() => handleAlign('right')}
                className="p-1 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded"
                title="Align Right"
              >
                <AlignRight className="w-4 h-4" />
              </button>
              
              <div className="w-px h-4 bg-gray-300 mx-1"></div>
              
              <button
                onClick={() => handleAlign('top')}
                className="p-1 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded"
                title="Align Top"
              >
                <AlignHorizontalJustifyCenter className="w-4 h-4 rotate-90" />
              </button>
              
              <button
                onClick={() => handleAlign('center-v')}
                className="p-1 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded"
                title="Center Vertically"
              >
                <AlignVerticalJustifyCenter className="w-4 h-4" />
              </button>
              
              <button
                onClick={() => handleAlign('bottom')}
                className="p-1 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded"
                title="Align Bottom"
              >
                <AlignHorizontalJustifyCenter className="w-4 h-4 -rotate-90" />
              </button>
              
              {brandKits.length > 0 && (
                <>
                  <div className="w-px h-4 bg-gray-300 mx-1"></div>
                  <select
                    value={activeBrandKit?.id || ''}
                    onChange={(e) => {
                      const kit = brandKits.find(k => k.id === e.target.value);
                      if (kit) handleApplyBrandKit(kit);
                    }}
                    className="text-xs px-2 py-1 border border-gray-200 rounded"
                  >
                    <option value="">Apply Brand Kit</option>
                    {brandKits.map(kit => (
                      <option key={kit.id} value={kit.id}>{kit.name}</option>
                    ))}
                  </select>
                </>
              )}
            </div>
          )}
          
          {/* Canvas */}
          <div className="flex-1 p-4 overflow-auto">
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
        </div>
        
        {/* Properties Panel */}
        <div className="w-full md:w-80 bg-white border-l border-gray-200 flex flex-col">
          <PropertiesPanel
            template={template}
            editorState={editorState}
            selectedElements={selectedElements}
            activeTab={activeTab}
            onTabChange={setActiveTab}
            onPropertyChange={handlePropertyChange}
            onCanvasChange={handleCanvasChange}
            commandInput={commandInput}
            onCommandInputChange={setCommandInput}
            onCommandSubmit={handleCommandSubmit}
            brandKits={brandKits}
            onApplyBrandKit={handleApplyBrandKit}
          />
        </div>
      </div>
    </div>
  );
};

export default EditorPage;