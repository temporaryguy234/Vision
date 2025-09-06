import React from 'react';

const SnapGuides = ({ guides, canvasWidth, canvasHeight }) => {
  if (!guides || (guides.x.length === 0 && guides.y.length === 0)) {
    return null;
  }
  
  return (
    <div className="absolute inset-0 pointer-events-none">
      {/* Vertical guides (X positions) */}
      {guides.x.map((xPercent, index) => (
        <div
          key={`x-guide-${index}`}
          className="absolute bg-orange-500/60 transition-opacity duration-200"
          style={{
            left: `${xPercent}%`,
            top: 0,
            width: '1px',
            height: '100%',
            transform: 'translateX(-0.5px)'
          }}
        />
      ))}
      
      {/* Horizontal guides (Y positions) */}
      {guides.y.map((yPercent, index) => (
        <div
          key={`y-guide-${index}`}
          className="absolute bg-orange-500/60 transition-opacity duration-200"
          style={{
            top: `${yPercent}%`,
            left: 0,
            height: '1px',
            width: '100%',
            transform: 'translateY(-0.5px)'
          }}
        />
      ))}
      
      {/* Grid lines for major positions */}
      <div className="absolute inset-0">
        {/* Center lines */}
        <div
          className="absolute bg-blue-300/30"
          style={{
            left: '50%',
            top: 0,
            width: '1px',
            height: '100%',
            transform: 'translateX(-0.5px)'
          }}
        />
        <div
          className="absolute bg-blue-300/30"
          style={{
            top: '50%',
            left: 0,
            height: '1px',
            width: '100%',
            transform: 'translateY(-0.5px)'
          }}
        />
        
        {/* Third lines */}
        <div
          className="absolute bg-blue-200/20"
          style={{
            left: '33.33%',
            top: 0,
            width: '1px',
            height: '100%',
            transform: 'translateX(-0.5px)'
          }}
        />
        <div
          className="absolute bg-blue-200/20"
          style={{
            left: '66.67%',
            top: 0,
            width: '1px',
            height: '100%',
            transform: 'translateX(-0.5px)'
          }}
        />
        <div
          className="absolute bg-blue-200/20"
          style={{
            top: '33.33%',
            left: 0,
            height: '1px',
            width: '100%',
            transform: 'translateY(-0.5px)'
          }}
        />
        <div
          className="absolute bg-blue-200/20"
          style={{
            top: '66.67%',
            left: 0,
            height: '1px',
            width: '100%',
            transform: 'translateY(-0.5px)'
          }}
        />
      </div>
    </div>
  );
};

export default SnapGuides;