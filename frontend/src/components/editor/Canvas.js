import React, { forwardRef, useRef, useEffect, useState, useCallback } from 'react';
import ElementRenderer from './ElementRenderer';
import SelectionBox from './SelectionBox';
import SnapGuides from './SnapGuides';
import LottieRenderer from './LottieRenderer';

const Canvas = forwardRef(({
  template,
  animationData,
  editorState,
  selectedElements,
  zoom,
  isPlaying,
  onElementSelect,
  onElementTransform,
  onCanvasChange
}, ref) => {
  const canvasRef = useRef(null);
  const [canvasDimensions, setCanvasDimensions] = useState({ width: 800, height: 450 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [snapGuides, setSnapGuides] = useState({ x: [], y: [] });
  
  // Calculate canvas dimensions based on template schema or animation data
  useEffect(() => {
    let width = 400, height = 400;
    
    if (template?.editable_parameters_schema?.canvas) {
      width = template.editable_parameters_schema.canvas.width;
      height = template.editable_parameters_schema.canvas.height;
    } else if (animationData) {
      width = animationData.w || 400;
      height = animationData.h || 400;
    }
    
    const aspectRatio = width / height;
    const maxWidth = 800;
    const maxHeight = 600;
    
    let canvasWidth, canvasHeight;
    
    if (aspectRatio > maxWidth / maxHeight) {
      canvasWidth = maxWidth;
      canvasHeight = maxWidth / aspectRatio;
    } else {
      canvasHeight = maxHeight;
      canvasWidth = maxHeight * aspectRatio;
    }
    
    setCanvasDimensions({ width: canvasWidth, height: canvasHeight });
  }, [template, animationData]);
  
  // Handle canvas click (deselect elements)
  const handleCanvasClick = useCallback((e) => {
    if (e.target === canvasRef.current) {
      onElementSelect(null, false);
    }
  }, [onElementSelect]);
  
  // Handle element click
  const handleElementClick = useCallback((elementId, e) => {
    e.stopPropagation();
    const multiSelect = e.shiftKey;
    onElementSelect(elementId, multiSelect);
  }, [onElementSelect]);
  
  // Handle drag start
  const handleDragStart = useCallback((elementId, e) => {
    if (!selectedElements.includes(elementId)) {
      onElementSelect(elementId, false);
    }
    
    setIsDragging(true);
    setDragStart({
      x: e.clientX,
      y: e.clientY
    });
    
    // Generate snap guides
    const guides = { x: [0, 50, 100], y: [0, 50, 100] };
    template?.editable_parameters_schema?.elements?.forEach(element => {
      const elementState = editorState.elements[element.id];
      if (elementState && !selectedElements.includes(element.id)) {
        if (elementState.x !== undefined) guides.x.push(elementState.x);
        if (elementState.y !== undefined) guides.y.push(elementState.y);
      }
    });
    
    setSnapGuides(guides);
  }, [selectedElements, onElementSelect, template, editorState]);
  
  // Handle drag move
  const handleDragMove = useCallback((e) => {
    if (!isDragging) return;
    
    const deltaX = e.clientX - dragStart.x;
    const deltaY = e.clientY - dragStart.y;
    
    // Convert to percentage based on canvas size
    const deltaXPercent = (deltaX / canvasDimensions.width) * 100;
    const deltaYPercent = (deltaY / canvasDimensions.height) * 100;
    
    selectedElements.forEach(elementId => {
      const currentElement = editorState.elements[elementId] || {};
      const newX = Math.max(0, Math.min(100, (currentElement.x || 50) + deltaXPercent));
      const newY = Math.max(0, Math.min(100, (currentElement.y || 50) + deltaYPercent));
      
      // Snap to guides
      const snapThreshold = 2; // 2% snap threshold
      const snappedX = snapGuides.x.find(guide => Math.abs(newX - guide) < snapThreshold) || newX;
      const snappedY = snapGuides.y.find(guide => Math.abs(newY - guide) < snapThreshold) || newY;
      
      onElementTransform(elementId, {
        x: snappedX,
        y: snappedY
      });
    });
    
    setDragStart({ x: e.clientX, y: e.clientY });
  }, [isDragging, dragStart, canvasDimensions, selectedElements, editorState, snapGuides, onElementTransform]);
  
  // Handle drag end
  const handleDragEnd = useCallback(() => {
    setIsDragging(false);
    setSnapGuides({ x: [], y: [] });
  }, []);
  
  // Handle scale
  const handleScale = useCallback((elementId, scale, maintainAspect = false) => {
    const currentElement = editorState.elements[elementId] || {};
    const newScale = Math.max(0.1, Math.min(5.0, scale));
    
    onElementTransform(elementId, {
      scale: newScale
    });
  }, [editorState, onElementTransform]);
  
  // Handle rotation
  const handleRotate = useCallback((elementId, rotation) => {
    const normalizedRotation = ((rotation % 360) + 360) % 360;
    
    onElementTransform(elementId, {
      rotation: normalizedRotation
    });
  }, [onElementTransform]);
  
  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (selectedElements.length === 0) return;
      
      switch (e.key) {
        case 'Delete':
        case 'Backspace':
          // TODO: Implement element deletion
          break;
        case 'ArrowLeft':
          e.preventDefault();
          selectedElements.forEach(elementId => {
            const current = editorState.elements[elementId] || {};
            onElementTransform(elementId, {
              x: Math.max(0, (current.x || 50) - (e.shiftKey ? 10 : 1))
            });
          });
          break;
        case 'ArrowRight':
          e.preventDefault();
          selectedElements.forEach(elementId => {
            const current = editorState.elements[elementId] || {};
            onElementTransform(elementId, {
              x: Math.min(100, (current.x || 50) + (e.shiftKey ? 10 : 1))
            });
          });
          break;
        case 'ArrowUp':
          e.preventDefault();
          selectedElements.forEach(elementId => {
            const current = editorState.elements[elementId] || {};
            onElementTransform(elementId, {
              y: Math.max(0, (current.y || 50) - (e.shiftKey ? 10 : 1))
            });
          });
          break;
        case 'ArrowDown':
          e.preventDefault();
          selectedElements.forEach(elementId => {
            const current = editorState.elements[elementId] || {};
            onElementTransform(elementId, {
              y: Math.min(100, (current.y || 50) + (e.shiftKey ? 10 : 1))
            });
          });
          break;
      }
    };
    
    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('mousemove', handleDragMove);
    document.addEventListener('mouseup', handleDragEnd);
    
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('mousemove', handleDragMove);
      document.removeEventListener('mouseup', handleDragEnd);
    };
  }, [selectedElements, editorState, onElementTransform, handleDragMove, handleDragEnd]);
  
  // Get canvas background style
  const getCanvasBackground = () => {
    const bgColor = editorState.canvas?.background_color || 
                   template?.editable_parameters_schema?.canvas?.background_color || 
                   '#FFFFFF';
    
    if (bgColor === 'transparent') {
      return {
        background: `
          linear-gradient(45deg, #f0f0f0 25%, transparent 25%),
          linear-gradient(-45deg, #f0f0f0 25%, transparent 25%),
          linear-gradient(45deg, transparent 75%, #f0f0f0 75%),
          linear-gradient(-45deg, transparent 75%, #f0f0f0 75%)
        `,
        backgroundSize: '20px 20px',
        backgroundPosition: '0 0, 0 10px, 10px -10px, -10px 0px'
      };
    }
    
    return { backgroundColor: bgColor };
  };
  
  if (!template && !animationData) return null;
  
  return (
    <div className="flex items-center justify-center min-h-full p-8">
      <div 
        className="relative shadow-2xl rounded-lg overflow-hidden border border-gray-300"
        style={{
          width: canvasDimensions.width * (zoom / 100),
          height: canvasDimensions.height * (zoom / 100),
          ...getCanvasBackground()
        }}
      >
        {/* Main Canvas */}
        <div
          ref={canvasRef}
          className="relative w-full h-full cursor-default"
          onClick={handleCanvasClick}
          style={{
            transform: `scale(${zoom / 100})`,
            transformOrigin: 'top left',
            width: canvasDimensions.width,
            height: canvasDimensions.height
          }}
        >
          {/* Render Main Lottie Animation */}
          {animationData && (
            <div
              className="absolute inset-0 w-full h-full flex items-center justify-center"
              style={{
                transform: `scale(${zoom / 100})`,
                transformOrigin: 'center center'
              }}
            >
              <LottieRenderer
                animationData={animationData}
                loop={true}
                autoplay={isPlaying}
                speed={editorState.canvas?.global_playback_speed || 1.0}
                isSelected={false}
                isPlaying={isPlaying}
                className="w-full h-full"
              />
            </div>
          )}
          
          {/* Render Editable Elements */}
          {(template.editable_parameters_schema?.elements || template.manifest?.elements || []).map(element => (
            <ElementRenderer
              key={element.id}
              element={element}
              elementState={editorState.elements[element.id] || {}}
              isSelected={selectedElements.includes(element.id)}
              isPlaying={isPlaying}
              onClick={(e) => handleElementClick(element.id, e)}
              onDragStart={(e) => handleDragStart(element.id, e)}
            />
          ))}
          
          {/* Selection Boxes */}
          {selectedElements.map(elementId => {
            const element = template.editable_parameters_schema?.elements?.find(e => e.id === elementId) ||
                           template.manifest?.elements?.find(e => e.id === elementId);
            const elementState = editorState.elements[elementId] || {};
            
            if (!element) return null;
            
            return (
              <SelectionBox
                key={`selection-${elementId}`}
                element={element}
                elementState={elementState}
                onScale={(scale, maintainAspect) => handleScale(elementId, scale, maintainAspect)}
                onRotate={(rotation) => handleRotate(elementId, rotation)}
              />
            );
          })}
          
          {/* Snap Guides */}
          <SnapGuides
            guides={snapGuides}
            canvasWidth={canvasDimensions.width}
            canvasHeight={canvasDimensions.height}
          />
        </div>
        
        {/* Canvas Info Overlay */}
        <div className="absolute top-2 left-2 bg-black/70 text-white px-2 py-1 rounded text-xs">
          {animationData ? `${animationData.w || 400} × ${animationData.h || 400}` : 
           `${template.editable_parameters_schema?.canvas?.width || template.manifest?.canvas?.width || 400} × ${template.editable_parameters_schema?.canvas?.height || template.manifest?.canvas?.height || 400}`}
          {isPlaying && <span className="ml-2">▶ Playing</span>}
        </div>
        
        {/* Speed Indicator */}
        {editorState.canvas?.global_playback_speed !== 1.0 && (
          <div className="absolute top-2 right-2 bg-orange-500 text-white px-2 py-1 rounded text-xs">
            {editorState.canvas.global_playback_speed}×
          </div>
        )}
      </div>
    </div>
  );
});

Canvas.displayName = 'Canvas';

export default Canvas;