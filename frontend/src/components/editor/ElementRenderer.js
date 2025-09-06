import React from 'react';
import { BarChart3, PieChart, TrendingUp, MapPin } from 'lucide-react';
import LottieRenderer from './LottieRenderer';

const ElementRenderer = ({ 
  element, 
  elementState, 
  isSelected, 
  isPlaying,
  onClick,
  onDragStart 
}) => {
  // Merge default parameters with current state
  const params = { ...element.parameters, ...elementState };
  
  // Calculate position and transform
  const getElementStyle = () => {
    const x = params.x !== undefined ? params.x : 50;
    const y = params.y !== undefined ? params.y : 50;
    const scale = params.scale !== undefined ? params.scale : 1;
    const rotation = params.rotation !== undefined ? params.rotation : 0;
    const opacity = params.opacity !== undefined ? params.opacity : 1;
    
    return {
      position: 'absolute',
      left: `${x}%`,
      top: `${y}%`,
      transform: `translate(-50%, -50%) scale(${scale}) rotate(${rotation}deg)`,
      opacity,
      cursor: 'pointer',
      zIndex: isSelected ? 10 : 1,
      pointerEvents: 'auto'
    };
  };
  
  // Render text element
  const renderTextElement = () => {
    const fontSize = params.font_size || 24;
    const color = params.color || '#000000';
    const fontFamily = params.font_family || 'Inter';
    const alignment = params.alignment || 'center';
    const content = params.content || 'Text';
    
    return (
      <div
        className={`select-none whitespace-nowrap ${isSelected ? 'ring-2 ring-orange-500' : ''}`}
        style={{
          fontSize: `${fontSize}px`,
          color,
          fontFamily,
          textAlign: alignment,
          fontWeight: '500'
        }}
      >
        {content}
      </div>
    );
  };
  
  // Render image element
  const renderImageElement = () => {
    const sourceUrl = params.source_url || 'https://placeholder.com/300x200';
    const fit = params.fit || 'cover';
    
    return (
      <div 
        className={`w-24 h-24 border-2 border-dashed border-gray-300 bg-gray-100 flex items-center justify-center overflow-hidden rounded ${isSelected ? 'ring-2 ring-orange-500' : ''}`}
      >
        <img
          src={sourceUrl}
          alt={element.name}
          className="max-w-full max-h-full"
          style={{
            objectFit: fit
          }}
          onError={(e) => {
            e.target.style.display = 'none';
            e.target.nextSibling.style.display = 'flex';
          }}
        />
        <div className="hidden w-full h-full bg-gray-200 items-center justify-center">
          <span className="text-gray-500 text-xs">Image</span>
        </div>
      </div>
    );
  };
  
  // Render shape element
  const renderShapeElement = () => {
    const fillColor = params.fill_color || '#0000FF';
    const strokeColor = params.stroke_color;
    const strokeWidth = params.stroke_width || 0;
    const cornerRadius = params.corner_radius || 0;
    
    return (
      <div
        className={`w-24 h-16 ${isSelected ? 'ring-2 ring-orange-500' : ''}`}
        style={{
          backgroundColor: fillColor,
          border: strokeColor ? `${strokeWidth}px solid ${strokeColor}` : 'none',
          borderRadius: `${cornerRadius}px`
        }}
      />
    );
  };
  
  // Render chart element
  const renderChartElement = () => {
    const chartType = params.chart_type || 'bar';
    const seriesColors = params.series_colors || ['#3B82F6', '#EF4444', '#10B981'];
    const data = params.data_placeholder || [10, 20, 30, 40];
    const showLabels = params.show_labels !== false;
    
    const maxValue = Math.max(...data);
    
    return (
      <div className={`w-32 h-24 bg-white border border-gray-200 rounded p-2 ${isSelected ? 'ring-2 ring-orange-500' : ''}`}>
        <div className="flex items-end justify-around h-full">
          {chartType === 'bar' && data.map((value, index) => (
            <div key={index} className="flex flex-col items-center">
              <div
                className="w-4 rounded-t"
                style={{
                  height: `${(value / maxValue) * 60}px`,
                  backgroundColor: seriesColors[index % seriesColors.length],
                  minHeight: '2px'
                }}
              />
              {showLabels && (
                <span className="text-xs text-gray-600 mt-1">{value}</span>
              )}
            </div>
          ))}
          
          {chartType === 'line' && (
            <svg width="100%" height="60" className="overflow-visible">
              <polyline
                fill="none"
                stroke={seriesColors[0]}
                strokeWidth={params.line_width || 2}
                points={data.map((value, index) => 
                  `${(index / (data.length - 1)) * 100},${60 - (value / maxValue) * 60}`
                ).join(' ')}
              />
              {data.map((value, index) => (
                <circle
                  key={index}
                  cx={(index / (data.length - 1)) * 100}
                  cy={60 - (value / maxValue) * 60}
                  r="2"
                  fill={seriesColors[0]}
                />
              ))}
            </svg>
          )}
          
          {chartType === 'pie' && (
            <div className="w-12 h-12 rounded-full border-4 border-gray-300 flex items-center justify-center">
              <PieChart className="w-6 h-6 text-gray-600" />
            </div>
          )}
        </div>
        
        {chartType === 'bar' && <BarChart3 className="absolute top-1 right-1 w-3 h-3 text-gray-400" />}
        {chartType === 'line' && <TrendingUp className="absolute top-1 right-1 w-3 h-3 text-gray-400" />}
      </div>
    );
  };
  
  // Render map element
  const renderMapElement = () => {
    const focusRegion = params.focus_region || 'world';
    const landColor = params.land_color || '#10B981';
    const borderColor = params.border_color || '#374151';
    const borderWidth = params.border_width || 1;
    const showLabels = params.show_labels !== false;
    
    return (
      <div className={`w-32 h-20 bg-blue-50 border border-gray-200 rounded flex items-center justify-center relative ${isSelected ? 'ring-2 ring-orange-500' : ''}`}>
        {/* Simplified world map representation */}
        <svg width="100%" height="100%" viewBox="0 0 128 80" className="absolute inset-0">
          {/* Continents as simple shapes */}
          <path
            d="M20,25 L35,20 L45,30 L55,25 L60,35 L45,40 L30,45 L20,35 Z"
            fill={landColor}
            stroke={borderColor}
            strokeWidth={borderWidth}
          />
          <path
            d="M70,30 L85,25 L95,35 L100,30 L105,40 L95,45 L80,50 L70,40 Z"
            fill={landColor}
            stroke={borderColor}
            strokeWidth={borderWidth}
          />
          <path
            d="M25,55 L40,50 L50,60 L45,65 L30,65 L25,60 Z"
            fill={landColor}
            stroke={borderColor}
            strokeWidth={borderWidth}
          />
        </svg>
        
        <MapPin className="absolute top-1 right-1 w-3 h-3 text-gray-600" />
        
        {showLabels && (
          <div className="absolute bottom-1 left-1 text-xs text-gray-600 bg-white/80 px-1 rounded">
            {focusRegion}
          </div>
        )}
      </div>
    );
  };

  // Render Lottie element
  const renderLottieElement = () => {
    const sourceUrl = params.source_url;
    const loop = params.loop !== false;
    const autoplay = params.autoplay !== false;
    const speed = params.speed || 1.0;
    
    return (
      <LottieRenderer
        sourceUrl={sourceUrl}
        loop={loop}
        autoplay={autoplay}
        speed={speed}
        isSelected={isSelected}
        isPlaying={isPlaying}
        onClick={onClick}
        onDragStart={onDragStart}
      />
    );
  };
  
  // Render appropriate element type
  const renderElement = () => {
    switch (element.type) {
      case 'text':
        return renderTextElement();
      case 'image':
        return renderImageElement();
      case 'shape':
        return renderShapeElement();
      case 'chart':
        return renderChartElement();
      case 'map':
        return renderMapElement();
      case 'lottie':
        return renderLottieElement();
      default:
        return (
          <div className={`w-16 h-16 bg-gray-200 border border-gray-300 rounded flex items-center justify-center ${isSelected ? 'ring-2 ring-orange-500' : ''}`}>
            <span className="text-xs text-gray-500">{element.type}</span>
          </div>
        );
    }
  };
  
  // Handle entrance animation
  const getAnimationStyle = () => {
    if (!isPlaying || !params.entrance_animation) {
      return {};
    }
    
    const animation = params.entrance_animation;
    const delay = animation.delay || 0;
    const duration = animation.duration || 1;
    
    let animationName = '';
    switch (animation.type) {
      case 'fade-in':
        animationName = 'fadeIn';
        break;
      case 'fly-in-left':
        animationName = 'slideInLeft';
        break;
      case 'fly-in-right':
        animationName = 'slideInRight';
        break;
      case 'fly-in-top':
        animationName = 'slideInDown';
        break;
      case 'fly-in-bottom':
        animationName = 'slideInUp';
        break;
      case 'scale-in':
        animationName = 'zoomIn';
        break;
      case 'bounce-in':
        animationName = 'bounceIn';
        break;
      default:
        animationName = 'fadeIn';
    }
    
    return {
      animation: `${animationName} ${duration}s ${animation.easing || 'ease'} ${delay}s both`
    };
  };
  
  return (
    <div
      className="editor-element"
      style={{
        ...getElementStyle(),
        ...getAnimationStyle()
      }}
      onClick={onClick}
      onMouseDown={onDragStart}
      title={element.name}
    >
      {renderElement()}
      
      {/* Element label for debugging */}
      {process.env.NODE_ENV === 'development' && (
        <div className="absolute -top-5 left-0 text-xs bg-black text-white px-1 rounded opacity-50">
          {element.id}
        </div>
      )}
    </div>
  );
};

export default ElementRenderer;