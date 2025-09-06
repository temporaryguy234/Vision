import React, { useState, useCallback } from 'react';
import { 
  Type, 
  Image, 
  Square, 
  BarChart3, 
  MapPin, 
  Palette,
  Play,
  Settings,
  ChevronDown,
  ChevronRight
} from 'lucide-react';

const PropertiesPanel = ({
  template,
  editorState,
  selectedElements,
  activeTab,
  onTabChange,
  onPropertyChange,
  onCanvasChange,
  commandInput,
  onCommandInputChange,
  onCommandSubmit,
  brandKits,
  onApplyBrandKit
}) => {
  const [expandedSections, setExpandedSections] = useState({
    canvas: true,
    elements: true,
    animation: false
  });
  
  const tabs = ['Content', 'Style', 'Animation'];
  
  // Toggle section expansion
  const toggleSection = useCallback((section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  }, []);
  
  // Get element icon
  const getElementIcon = (type) => {
    switch (type) {
      case 'text': return Type;
      case 'image': return Image;
      case 'shape': return Square;
      case 'chart': return BarChart3;
      case 'map': return MapPin;
      default: return Settings;
    }
  };
  
  // Validate property value
  const validateProperty = (element, property, value) => {
    // Basic validation based on property type
    switch (property) {
      case 'font_size':
        const size = parseInt(value);
        return size >= 12 && size <= 180 ? null : 'Font size must be between 12 and 180 pixels';
      
      case 'color':
      case 'fill_color':
      case 'stroke_color':
      case 'land_color':
      case 'border_color':
        return /^#[0-9A-Fa-f]{6}$/.test(value) ? null : 'Must be a valid hex color (#RRGGBB)';
      
      case 'opacity':
        const opacity = parseFloat(value);
        return opacity >= 0 && opacity <= 1 ? null : 'Opacity must be between 0 and 1';
      
      case 'x':
      case 'y':
        const pos = parseFloat(value);
        return pos >= 0 && pos <= 100 ? null : 'Position must be between 0 and 100 percent';
      
      case 'scale':
        const scale = parseFloat(value);
        return scale >= 0.1 && scale <= 5.0 ? null : 'Scale must be between 0.1 and 5.0';
      
      case 'rotation':
        const rotation = parseFloat(value);
        return rotation >= -360 && rotation <= 360 ? null : 'Rotation must be between -360 and 360 degrees';
      
      case 'stroke_width':
        const strokeWidth = parseInt(value);
        return strokeWidth >= 0 && strokeWidth <= 20 ? null : 'Stroke width must be between 0 and 20 pixels';
      
      case 'border_width':
        const borderWidth = parseInt(value);
        return borderWidth >= 0 && borderWidth <= 12 ? null : 'Border width must be between 0 and 12 pixels';
      
      case 'content':
        return value.length <= 500 ? null : 'Text content must not exceed 500 characters';
      
      default:
        return null;
    }
  };
  
  // Handle property change with validation
  const handlePropertyChange = useCallback((elementId, property, value) => {
    const element = template?.editable_parameters_schema.elements.find(e => e.id === elementId);
    if (!element) return;
    
    const error = validateProperty(element, property, value);
    if (error) {
      // TODO: Show error message
      console.warn(`Validation error for ${property}:`, error);
      return;
    }
    
    const oldValue = editorState.elements[elementId]?.[property] || element.parameters[property];
    onPropertyChange(elementId, property, value, oldValue);
  }, [template, editorState, onPropertyChange]);
  
  // Handle canvas property change
  const handleCanvasPropertyChange = useCallback((property, value) => {
    const oldValue = editorState.canvas?.[property] || template?.editable_parameters_schema.canvas[property];
    onCanvasChange(property, value, oldValue);
  }, [editorState, template, onCanvasChange]);
  
  // Render property input
  const renderPropertyInput = (element, property, label, type = 'text', options = {}) => {
    const currentValue = editorState.elements[element.id]?.[property] || element.parameters[property];
    const elementId = element.id;
    
    const inputProps = {
      value: currentValue || '',
      onChange: (e) => handlePropertyChange(elementId, property, e.target.value),
      className: "w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-300"
    };
    
    switch (type) {
      case 'number':
        return (
          <input
            type="number"
            {...inputProps}
            {...options}
          />
        );
      
      case 'range':
        return (
          <div className="flex items-center space-x-2">
            <input
              type="range"
              {...inputProps}
              className="flex-1"
              {...options}
            />
            <span className="text-sm text-gray-600 w-12 text-right">
              {options.unit ? `${currentValue}${options.unit}` : currentValue}
            </span>
          </div>
        );
      
      case 'color':
        return (
          <div className="flex items-center space-x-2">
            <input
              type="color"
              value={currentValue || '#000000'}
              onChange={(e) => handlePropertyChange(elementId, property, e.target.value)}
              className="w-12 h-8 border border-gray-200 rounded cursor-pointer"
            />
            <input
              type="text"
              {...inputProps}
              placeholder="#000000"
              className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-300"
            />
          </div>
        );
      
      case 'select':
        return (
          <select
            {...inputProps}
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-300"
          >
            {options.options?.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        );
      
      case 'textarea':
        return (
          <textarea
            {...inputProps}
            rows={3}
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-300 resize-none"
          />
        );
      
      default:
        return <input type="text" {...inputProps} />;
    }
  };
  
  // Render content properties
  const renderContentProperties = (element) => {
    const properties = [];
    
    switch (element.type) {
      case 'text':
        properties.push(
          { key: 'content', label: 'Text Content', type: 'textarea' },
          { key: 'font_family', label: 'Font Family', type: 'select', options: {
            options: [
              { value: 'Inter', label: 'Inter' },
              { value: 'Roboto', label: 'Roboto' },
              { value: 'Montserrat', label: 'Montserrat' },
              { value: 'Poppins', label: 'Poppins' },
              { value: 'Open Sans', label: 'Open Sans' }
            ]
          }},
          { key: 'font_size', label: 'Font Size', type: 'number', options: { min: 12, max: 180, unit: 'px' } },
          { key: 'alignment', label: 'Alignment', type: 'select', options: {
            options: [
              { value: 'left', label: 'Left' },
              { value: 'center', label: 'Center' },
              { value: 'right', label: 'Right' }
            ]
          }}
        );
        break;
      
      case 'image':
        properties.push(
          { key: 'source_url', label: 'Image URL', type: 'text' },
          { key: 'fit', label: 'Fit', type: 'select', options: {
            options: [
              { value: 'cover', label: 'Cover' },
              { value: 'contain', label: 'Contain' }
            ]
          }}
        );
        break;
      
      case 'chart':
        properties.push(
          { key: 'chart_type', label: 'Chart Type', type: 'select', options: {
            options: [
              { value: 'bar', label: 'Bar Chart' },
              { value: 'line', label: 'Line Chart' },
              { value: 'pie', label: 'Pie Chart' }
            ]
          }},
          { key: 'show_labels', label: 'Show Labels', type: 'select', options: {
            options: [
              { value: true, label: 'Yes' },
              { value: false, label: 'No' }
            ]
          }}
        );
        break;
      
      case 'map':
        properties.push(
          { key: 'focus_region', label: 'Focus Region', type: 'text' },
          { key: 'show_labels', label: 'Show Labels', type: 'select', options: {
            options: [
              { value: true, label: 'Yes' },
              { value: false, label: 'No' }
            ]
          }}
        );
        break;
    }
    
    return properties.map(prop => (
      <div key={prop.key} className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {prop.label}
        </label>
        {renderPropertyInput(element, prop.key, prop.label, prop.type, prop.options)}
      </div>
    ));
  };
  
  // Render style properties
  const renderStyleProperties = (element) => {
    const properties = [];
    
    // Common properties
    properties.push(
      { key: 'opacity', label: 'Opacity', type: 'range', options: { min: 0, max: 1, step: 0.1, unit: '' } }
    );
    
    switch (element.type) {
      case 'text':
        properties.push(
          { key: 'color', label: 'Text Color', type: 'color' }
        );
        break;
      
      case 'shape':
        properties.push(
          { key: 'fill_color', label: 'Fill Color', type: 'color' },
          { key: 'stroke_color', label: 'Stroke Color', type: 'color' },
          { key: 'stroke_width', label: 'Stroke Width', type: 'number', options: { min: 0, max: 20, unit: 'px' } },
          { key: 'corner_radius', label: 'Corner Radius', type: 'number', options: { min: 0, max: 100, unit: 'px' } }
        );
        break;
      
      case 'chart':
        properties.push(
          { key: 'line_width', label: 'Line Width', type: 'number', options: { min: 0, max: 20, unit: 'px' } },
          { key: 'bar_width', label: 'Bar Width', type: 'number', options: { min: 1, max: 40, unit: 'px' } }
        );
        break;
      
      case 'map':
        properties.push(
          { key: 'land_color', label: 'Land Color', type: 'color' },
          { key: 'border_color', label: 'Border Color', type: 'color' },
          { key: 'border_width', label: 'Border Width', type: 'number', options: { min: 0, max: 12, unit: 'px' } }
        );
        break;
    }
    
    return properties.map(prop => (
      <div key={prop.key} className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {prop.label}
        </label>
        {renderPropertyInput(element, prop.key, prop.label, prop.type, prop.options)}
      </div>
    ));
  };
  
  // Render animation properties
  const renderAnimationProperties = (element) => {
    const currentAnimation = editorState.elements[element.id]?.entrance_animation || 
                           element.parameters.entrance_animation || {};
    
    return (
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Animation Type
          </label>
          <select
            value={currentAnimation.type || 'fade-in'}
            onChange={(e) => handlePropertyChange(element.id, 'entrance_animation', {
              ...currentAnimation,
              type: e.target.value
            })}
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-300"
          >
            <option value="fade-in">Fade In</option>
            <option value="fly-in-left">Fly In Left</option>
            <option value="fly-in-right">Fly In Right</option>
            <option value="fly-in-top">Fly In Top</option>
            <option value="fly-in-bottom">Fly In Bottom</option>
            <option value="scale-in">Scale In</option>
            <option value="bounce-in">Bounce In</option>
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Delay (seconds)
          </label>
          <input
            type="number"
            min="0"
            max="5"
            step="0.1"
            value={currentAnimation.delay || 0}
            onChange={(e) => handlePropertyChange(element.id, 'entrance_animation', {
              ...currentAnimation,
              delay: parseFloat(e.target.value)
            })}
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-300"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Duration (seconds)
          </label>
          <input
            type="number"
            min="0.5"
            max="5"
            step="0.1"
            value={currentAnimation.duration || 1}
            onChange={(e) => handlePropertyChange(element.id, 'entrance_animation', {
              ...currentAnimation,
              duration: parseFloat(e.target.value)
            })}
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-300"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Easing
          </label>
          <select
            value={currentAnimation.easing || 'ease'}
            onChange={(e) => handlePropertyChange(element.id, 'entrance_animation', {
              ...currentAnimation,
              easing: e.target.value
            })}
            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-300"
          >
            <option value="ease">Ease</option>
            <option value="ease-in">Ease In</option>
            <option value="ease-out">Ease Out</option>
            <option value="linear">Linear</option>
          </select>
        </div>
      </div>
    );
  };
  
  return (
    <div className="flex flex-col h-full">
      {/* Command Input (Desktop) */}
      <div className="hidden md:block border-b border-gray-200 p-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Natural Language Command
        </label>
        <div className="flex items-center space-x-2">
          <input
            type="text"
            placeholder="Type a command..."
            value={commandInput}
            onChange={(e) => onCommandInputChange(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && onCommandSubmit()}
            className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-300"
          />
          <button
            onClick={onCommandSubmit}
            className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors text-sm"
          >
            Run
          </button>
        </div>
      </div>
      
      {/* Tabs */}
      <div className="flex border-b border-gray-200">
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => onTabChange(tab)}
            className={`flex-1 py-3 px-4 text-sm font-medium transition-colors ${
              activeTab === tab
                ? 'text-orange-600 border-b-2 border-orange-500 bg-orange-50/50'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>
      
      {/* Properties Content */}
      <div className="flex-1 overflow-y-auto">
        {/* Canvas Properties */}
        <div className="border-b border-gray-200">
          <button
            onClick={() => toggleSection('canvas')}
            className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
          >
            <span className="font-medium text-gray-900">Canvas</span>
            {expandedSections.canvas ? 
              <ChevronDown className="w-4 h-4 text-gray-500" /> : 
              <ChevronRight className="w-4 h-4 text-gray-500" />
            }
          </button>
          
          {expandedSections.canvas && (
            <div className="px-4 pb-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Background Color
                </label>
                <div className="flex items-center space-x-2">
                  <input
                    type="color"
                    value={editorState.canvas?.background_color === 'transparent' ? '#FFFFFF' : 
                           (editorState.canvas?.background_color || '#FFFFFF')}
                    onChange={(e) => handleCanvasPropertyChange('background_color', e.target.value)}
                    className="w-12 h-8 border border-gray-200 rounded cursor-pointer"
                  />
                  <input
                    type="text"
                    value={editorState.canvas?.background_color || '#FFFFFF'}
                    onChange={(e) => handleCanvasPropertyChange('background_color', e.target.value)}
                    placeholder="#FFFFFF or transparent"
                    className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-300"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Playback Speed
                </label>
                <div className="flex items-center space-x-2">
                  <input
                    type="range"
                    min="0.5"
                    max="2"
                    step="0.1"
                    value={editorState.canvas?.global_playback_speed || 1}
                    onChange={(e) => handleCanvasPropertyChange('global_playback_speed', parseFloat(e.target.value))}
                    className="flex-1"
                  />
                  <span className="text-sm text-gray-600 w-12 text-right">
                    {(editorState.canvas?.global_playback_speed || 1)}×
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* Element Properties */}
        {selectedElements.length > 0 && (
          <div className="border-b border-gray-200">
            <button
              onClick={() => toggleSection('elements')}
              className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
            >
              <span className="font-medium text-gray-900">
                Selected Elements ({selectedElements.length})
              </span>
              {expandedSections.elements ? 
                <ChevronDown className="w-4 h-4 text-gray-500" /> : 
                <ChevronRight className="w-4 h-4 text-gray-500" />
              }
            </button>
            
            {expandedSections.elements && (
              <div className="px-4 pb-4">
                {selectedElements.map(elementId => {
                  const element = template?.editable_parameters_schema.elements.find(e => e.id === elementId);
                  if (!element) return null;
                  
                  const Icon = getElementIcon(element.type);
                  
                  return (
                    <div key={elementId} className="mb-6 last:mb-0">
                      <div className="flex items-center mb-3 pb-2 border-b border-gray-100">
                        <Icon className="w-4 h-4 text-gray-600 mr-2" />
                        <span className="font-medium text-gray-900">{element.name}</span>
                        <span className="ml-2 text-xs text-gray-500 px-2 py-1 bg-gray-100 rounded">
                          {element.type}
                        </span>
                      </div>
                      
                      {activeTab === 'Content' && renderContentProperties(element)}
                      {activeTab === 'Style' && renderStyleProperties(element)}
                      {activeTab === 'Animation' && renderAnimationProperties(element)}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}
        
        {/* Brand Kits */}
        {brandKits.length > 0 && (
          <div className="p-4">
            <h4 className="font-medium text-gray-900 mb-3">Brand Kits</h4>
            <div className="space-y-2">
              {brandKits.map(kit => (
                <button
                  key={kit.id}
                  onClick={() => onApplyBrandKit(kit)}
                  className="w-full text-left p-3 border border-gray-200 rounded-lg hover:border-orange-300 hover:bg-orange-50/50 transition-colors"
                  disabled={selectedElements.length === 0}
                >
                  <div className="font-medium text-gray-900">{kit.name}</div>
                  <div className="flex items-center mt-1 space-x-1">
                    {kit.colors.slice(0, 5).map((color, index) => (
                      <div
                        key={index}
                        className="w-3 h-3 rounded-full border border-gray-200"
                        style={{ backgroundColor: color }}
                      />
                    ))}
                    {kit.colors.length > 5 && (
                      <span className="text-xs text-gray-500">+{kit.colors.length - 5}</span>
                    )}
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}
        
        {/* No Selection State */}
        {selectedElements.length === 0 && (
          <div className="p-4 text-center text-gray-500">
            <Settings className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p className="text-sm">Select an element to edit its properties</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default PropertiesPanel;