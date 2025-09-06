import React, { useState, useCallback } from 'react';
import { RotateCw } from 'lucide-react';

const SelectionBox = ({ element, elementState, onScale, onRotate }) => {
  const [isResizing, setIsResizing] = useState(false);
  const [isRotating, setIsRotating] = useState(false);
  const [resizeStart, setResizeStart] = useState({ x: 0, y: 0, scale: 1 });
  const [rotateStart, setRotateStart] = useState({ angle: 0, rotation: 0 });
  
  // Merge default parameters with current state
  const params = { ...element.parameters, ...elementState };
  
  // Calculate position and transform
  const x = params.x !== undefined ? params.x : 50;
  const y = params.y !== undefined ? params.y : 50;
  const scale = params.scale !== undefined ? params.scale : 1;
  const rotation = params.rotation !== undefined ? params.rotation : 0;
  
  // Get bounding box style
  const getBoundingBoxStyle = () => {
    return {
      position: 'absolute',
      left: `${x}%`,
      top: `${y}%`,
      transform: `translate(-50%, -50%) scale(${scale}) rotate(${rotation}deg)`,
      transformOrigin: 'center center',
      pointerEvents: 'none',
      zIndex: 20
    };
  };
  
  // Handle resize start
  const handleResizeStart = useCallback((e, corner) => {
    e.stopPropagation();
    setIsResizing(true);
    setResizeStart({
      x: e.clientX,
      y: e.clientY,
      scale: scale
    });
    
    const handleResizeMove = (moveEvent) => {
      const deltaX = moveEvent.clientX - resizeStart.x;
      const deltaY = moveEvent.clientY - resizeStart.y;
      
      // Calculate scale based on drag distance
      const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
      const scaleFactor = 1 + (distance / 100); // Adjust sensitivity
      
      let newScale;
      if (corner === 'se' || corner === 'nw') {
        // Diagonal corners - positive scaling
        newScale = resizeStart.scale * (deltaX > 0 || deltaY > 0 ? scaleFactor : 1 / scaleFactor);
      } else {
        // Other corners
        newScale = resizeStart.scale * scaleFactor;
      }
      
      newScale = Math.max(0.1, Math.min(5.0, newScale));
      onScale(newScale, moveEvent.shiftKey);
    };
    
    const handleResizeEnd = () => {
      setIsResizing(false);
      document.removeEventListener('mousemove', handleResizeMove);
      document.removeEventListener('mouseup', handleResizeEnd);
    };
    
    document.addEventListener('mousemove', handleResizeMove);
    document.addEventListener('mouseup', handleResizeEnd);
  }, [scale, resizeStart.x, resizeStart.y, resizeStart.scale, onScale]);
  
  // Handle rotation start
  const handleRotationStart = useCallback((e) => {
    e.stopPropagation();
    setIsRotating(true);
    
    // Get element center
    const elementRect = e.currentTarget.parentElement.getBoundingClientRect();
    const centerX = elementRect.left + elementRect.width / 2;
    const centerY = elementRect.top + elementRect.height / 2;
    
    // Calculate initial angle
    const startAngle = Math.atan2(e.clientY - centerY, e.clientX - centerX);
    
    setRotateStart({
      angle: startAngle,
      rotation: rotation
    });
    
    const handleRotateMove = (moveEvent) => {
      const currentAngle = Math.atan2(moveEvent.clientY - centerY, moveEvent.clientX - centerX);
      const deltaAngle = currentAngle - rotateStart.angle;
      const deltaRotation = (deltaAngle * 180) / Math.PI;
      
      let newRotation = rotateStart.rotation + deltaRotation;
      
      // Snap to 15-degree increments if Shift is held
      if (moveEvent.shiftKey) {
        newRotation = Math.round(newRotation / 15) * 15;
      }
      
      onRotate(newRotation);
    };
    
    const handleRotateEnd = () => {
      setIsRotating(false);
      document.removeEventListener('mousemove', handleRotateMove);
      document.removeEventListener('mouseup', handleRotateEnd);
    };
    
    document.addEventListener('mousemove', handleRotateMove);
    document.addEventListener('mouseup', handleRotateEnd);
  }, [rotation, rotateStart.angle, rotateStart.rotation, onRotate]);
  
  return (
    <div style={getBoundingBoxStyle()}>
      {/* Main bounding box */}
      <div className="relative">
        {/* Selection outline */}
        <div 
          className="absolute border-2 border-orange-500 border-dashed bg-orange-500/5"
          style={{
            width: '120px',
            height: '80px',
            left: '50%',
            top: '50%',
            transform: 'translate(-50%, -50%)'
          }}
        />
        
        {/* Corner resize handles */}
        <div
          className="absolute w-3 h-3 bg-orange-500 border border-white rounded-sm cursor-nw-resize hover:bg-orange-600 transition-colors"
          style={{
            left: '50%',
            top: '50%',
            transform: 'translate(-60px, -40px)',
            pointerEvents: 'auto'
          }}
          onMouseDown={(e) => handleResizeStart(e, 'nw')}
          title="Resize (Shift: maintain aspect ratio)"
        />
        
        <div
          className="absolute w-3 h-3 bg-orange-500 border border-white rounded-sm cursor-ne-resize hover:bg-orange-600 transition-colors"
          style={{
            left: '50%',
            top: '50%',
            transform: 'translate(60px, -40px)',
            pointerEvents: 'auto'
          }}
          onMouseDown={(e) => handleResizeStart(e, 'ne')}
          title="Resize (Shift: maintain aspect ratio)"
        />
        
        <div
          className="absolute w-3 h-3 bg-orange-500 border border-white rounded-sm cursor-sw-resize hover:bg-orange-600 transition-colors"
          style={{
            left: '50%',
            top: '50%',
            transform: 'translate(-60px, 40px)',
            pointerEvents: 'auto'
          }}
          onMouseDown={(e) => handleResizeStart(e, 'sw')}
          title="Resize (Shift: maintain aspect ratio)"
        />
        
        <div
          className="absolute w-3 h-3 bg-orange-500 border border-white rounded-sm cursor-se-resize hover:bg-orange-600 transition-colors"
          style={{
            left: '50%',
            top: '50%',
            transform: 'translate(60px, 40px)',
            pointerEvents: 'auto'
          }}
          onMouseDown={(e) => handleResizeStart(e, 'se')}
          title="Resize (Shift: maintain aspect ratio)"
        />
        
        {/* Rotation handle */}
        <div
          className="absolute w-6 h-6 bg-orange-500 border border-white rounded-full cursor-pointer hover:bg-orange-600 transition-colors flex items-center justify-center"
          style={{
            left: '50%',
            top: '50%',
            transform: 'translate(-12px, -60px)',
            pointerEvents: 'auto'
          }}
          onMouseDown={handleRotationStart}
          title="Rotate (Shift: snap to 15° increments)"
        >
          <RotateCw className="w-3 h-3 text-white" />
        </div>
        
        {/* Rotation line */}
        <div
          className="absolute w-px h-5 bg-orange-500"
          style={{
            left: '50%',
            top: '50%',
            transform: 'translate(-0.5px, -55px)'
          }}
        />
        
        {/* Side handles for aspect-locked scaling */}
        <div
          className="absolute w-3 h-3 bg-orange-500 border border-white rounded-sm cursor-ew-resize hover:bg-orange-600 transition-colors"
          style={{
            left: '50%',
            top: '50%',
            transform: 'translate(60px, -12px)',
            pointerEvents: 'auto'
          }}
          onMouseDown={(e) => handleResizeStart(e, 'e')}
          title="Resize horizontally"
        />
        
        <div
          className="absolute w-3 h-3 bg-orange-500 border border-white rounded-sm cursor-ew-resize hover:bg-orange-600 transition-colors"
          style={{
            left: '50%',
            top: '50%',
            transform: 'translate(-60px, -12px)',
            pointerEvents: 'auto'
          }}
          onMouseDown={(e) => handleResizeStart(e, 'w')}
          title="Resize horizontally"
        />
        
        <div
          className="absolute w-3 h-3 bg-orange-500 border border-white rounded-sm cursor-ns-resize hover:bg-orange-600 transition-colors"
          style={{
            left: '50%',
            top: '50%',
            transform: 'translate(-12px, 40px)',
            pointerEvents: 'auto'
          }}
          onMouseDown={(e) => handleResizeStart(e, 's')}
          title="Resize vertically"
        />
        
        <div
          className="absolute w-3 h-3 bg-orange-500 border border-white rounded-sm cursor-ns-resize hover:bg-orange-600 transition-colors"
          style={{
            left: '50%',
            top: '50%',
            transform: 'translate(-12px, -40px)',
            pointerEvents: 'auto'
          }}
          onMouseDown={(e) => handleResizeStart(e, 'n')}
          title="Resize vertically"
        />
        
        {/* Element info */}
        <div
          className="absolute bg-orange-500 text-white px-2 py-1 rounded text-xs font-medium whitespace-nowrap"
          style={{
            left: '50%',
            top: '50%',
            transform: 'translate(-50%, -100px)'
          }}
        >
          {element.name}
          <span className="ml-2 opacity-75">
            {Math.round(scale * 100)}% • {Math.round(rotation)}°
          </span>
        </div>
        
        {/* Transform feedback */}
        {(isResizing || isRotating) && (
          <div
            className="absolute bg-black/75 text-white px-2 py-1 rounded text-xs font-medium whitespace-nowrap"
            style={{
              left: '50%',
              top: '50%',
              transform: 'translate(-50%, 60px)'
            }}
          >
            {isResizing && `Scale: ${Math.round(scale * 100)}%`}
            {isRotating && `Rotation: ${Math.round(rotation)}°`}
          </div>
        )}
      </div>
    </div>
  );
};

export default SelectionBox;