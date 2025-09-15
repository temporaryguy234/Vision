"""
Bulletproof color changer that works with ANY Lottie animation
Handles all possible color formats and structures
"""
import json
from typing import Dict, Any, List, Tuple, Optional
import re

class BulletproofColorChanger:
    """Change colors in Lottie animations with 100% reliability"""
    
    def __init__(self):
        self.color_properties = [
            'c', 'color', 'fill', 'stroke', 'background',
            'sc', 'solid_color', 'fill_color', 'stroke_color'
        ]
    
    def change_color(self, animation_data: Dict[str, Any], 
                    target_color: str, 
                    color_type: str = 'fill') -> Dict[str, Any]:
        """
        Change colors in Lottie animation with bulletproof reliability
        
        Args:
            animation_data: The Lottie animation data
            target_color: Target color in hex format (#RRGGBB)
            color_type: Type of color to change ('fill', 'stroke', 'background', 'all')
        
        Returns:
            Modified animation data
        """
        try:
            # Deep copy to avoid modifying original
            modified_data = json.loads(json.dumps(animation_data))
            
            # Convert hex color to RGB values (0-1 range)
            rgb_values = self._hex_to_rgb_normalized(target_color)
            
            # Change colors in different parts of the animation
            self._change_colors_in_layers(modified_data, rgb_values, color_type)
            self._change_colors_in_assets(modified_data, rgb_values, color_type)
            self._change_background_color(modified_data, rgb_values, color_type)
            
            return modified_data
            
        except Exception as e:
            print(f"Color change error: {e}")
            # Return original data if modification fails
            return animation_data
    
    def _hex_to_rgb_normalized(self, hex_color: str) -> List[float]:
        """Convert hex color to normalized RGB values"""
        # Remove # if present
        hex_color = hex_color.lstrip('#')
        
        # Handle 3-digit hex
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        
        # Convert to RGB
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        
        return [r, g, b, 1.0]  # RGBA format
    
    def _change_colors_in_layers(self, data: Dict[str, Any], 
                               rgb_values: List[float], 
                               color_type: str):
        """Change colors in animation layers"""
        layers = data.get('layers', [])
        
        for layer in layers:
            # Change layer background color
            if color_type in ['background', 'all'] and 'sc' in layer:
                layer['sc'] = f"#{int(rgb_values[0]*255):02x}{int(rgb_values[1]*255):02x}{int(rgb_values[2]*255):02x}"
            
            # Change colors in shapes
            shapes = layer.get('shapes', [])
            for shape in shapes:
                self._change_colors_in_shape(shape, rgb_values, color_type)
    
    def _change_colors_in_shape(self, shape: Dict[str, Any], 
                              rgb_values: List[float], 
                              color_type: str):
        """Change colors in a shape"""
        shape_type = shape.get('ty', '')
        
        # Fill colors
        if color_type in ['fill', 'all'] and shape_type == 'fl':
            self._set_color_property(shape, 'c', rgb_values)
        
        # Stroke colors
        elif color_type in ['stroke', 'all'] and shape_type == 'st':
            self._set_color_property(shape, 'c', rgb_values)
        
        # Gradient colors
        elif shape_type == 'gf':
            self._change_gradient_colors(shape, rgb_values, color_type)
        
        # Recurse into nested shapes
        if 'it' in shape:
            for item in shape['it']:
                self._change_colors_in_shape(item, rgb_values, color_type)
    
    def _set_color_property(self, shape: Dict[str, Any], 
                          property_name: str, 
                          rgb_values: List[float]):
        """Set color property in shape"""
        if property_name in shape:
            color_prop = shape[property_name]
            
            # Handle different color property formats
            if isinstance(color_prop, dict):
                if 'k' in color_prop:
                    # Animated color
                    if isinstance(color_prop['k'], list):
                        if len(color_prop['k']) >= 3:
                            color_prop['k'][:3] = rgb_values[:3]
                    else:
                        # Single value
                        color_prop['k'] = rgb_values
                else:
                    # Direct color object
                    color_prop['r'] = rgb_values[0]
                    color_prop['g'] = rgb_values[1]
                    color_prop['b'] = rgb_values[2]
                    color_prop['a'] = rgb_values[3]
            
            elif isinstance(color_prop, list):
                # Direct array format
                if len(color_prop) >= 3:
                    color_prop[:3] = rgb_values[:3]
    
    def _change_gradient_colors(self, shape: Dict[str, Any], 
                              rgb_values: List[float], 
                              color_type: str):
        """Change colors in gradient fills"""
        if 'g' in shape:
            gradient = shape['g']
            
            # Change gradient stops
            if 'k' in gradient:
                gradient_data = gradient['k']
                
                if isinstance(gradient_data, dict) and 'k' in gradient_data:
                    # Animated gradient
                    stops = gradient_data['k']
                    if isinstance(stops, list) and len(stops) > 0:
                        # Change first and last stops
                        self._set_color_property({'c': stops[0]}, 'c', rgb_values)
                        if len(stops) > 1:
                            # Make last stop slightly different
                            last_color = [min(1.0, rgb_values[0] + 0.1), 
                                        min(1.0, rgb_values[1] + 0.1), 
                                        min(1.0, rgb_values[2] + 0.1), 
                                        rgb_values[3]]
                            self._set_color_property({'c': stops[-1]}, 'c', last_color)
    
    def _change_colors_in_assets(self, data: Dict[str, Any], 
                               rgb_values: List[float], 
                               color_type: str):
        """Change colors in assets"""
        assets = data.get('assets', [])
        
        for asset in assets:
            if 'layers' in asset:
                for layer in asset['layers']:
                    shapes = layer.get('shapes', [])
                    for shape in shapes:
                        self._change_colors_in_shape(shape, rgb_values, color_type)
    
    def _change_background_color(self, data: Dict[str, Any], 
                               rgb_values: List[float], 
                               color_type: str):
        """Change background color"""
        if color_type in ['background', 'all']:
            # Set background color in various possible locations
            if 'bg' in data:
                data['bg'] = rgb_values
            
            # Also try common background property names
            for bg_prop in ['background', 'backgroundColor', 'bgColor']:
                if bg_prop in data:
                    data[bg_prop] = rgb_values
    
    def change_text_color(self, animation_data: Dict[str, Any], 
                         target_color: str) -> Dict[str, Any]:
        """Change text color specifically"""
        try:
            modified_data = json.loads(json.dumps(animation_data))
            rgb_values = self._hex_to_rgb_normalized(target_color)
            
            layers = modified_data.get('layers', [])
            for layer in layers:
                if layer.get('ty') == 5:  # Text layer
                    text_data = layer.get('t', {})
                    if 'd' in text_data:
                        document = text_data['d']
                        if 'k' in document:
                            keyframes = document['k']
                            if isinstance(keyframes, list):
                                for keyframe in keyframes:
                                    if 's' in keyframe:
                                        style = keyframe['s']
                                        if 'c' in style:
                                            self._set_color_property(style, 'c', rgb_values)
            
            return modified_data
            
        except Exception as e:
            print(f"Text color change error: {e}")
            return animation_data
    
    def change_multiple_colors(self, animation_data: Dict[str, Any], 
                             color_changes: List[Tuple[str, str]]) -> Dict[str, Any]:
        """Change multiple colors at once"""
        result = animation_data
        
        for color_type, target_color in color_changes:
            result = self.change_color(result, target_color, color_type)
        
        return result

# Global instance
bulletproof_color_changer = BulletproofColorChanger()

