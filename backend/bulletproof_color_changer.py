"""
Bulletproof Color Changer
A robust module for changing colors in Lottie animation data
"""

import json
from typing import Dict, Any, List

class BulletproofColorChanger:
    """A bulletproof color changer that always works"""
    
    def __init__(self):
        self.color_cache = {}
    
    def change_color(self, animation_data: Dict[str, Any], target_color: str, color_type: str = 'fill') -> Dict[str, Any]:
        """
        Change colors in Lottie animation data
        Returns modified animation data
        """
        try:
            print(f"🎨 Changing {color_type} color to {target_color}")
            
            # Create a deep copy of the animation data
            modified_data = json.loads(json.dumps(animation_data))
            
            # Convert hex color to RGB
            rgb_color = self._hex_to_rgb(target_color)
            if not rgb_color:
                print(f"❌ Invalid color format: {target_color}")
                return animation_data
            
            # Normalize RGB to 0-1 range for Lottie
            normalized_color = [rgb_color[0]/255.0, rgb_color[1]/255.0, rgb_color[2]/255.0, 1.0]
            
            # Apply color changes based on type
            if color_type == 'fill':
                self._change_fill_colors(modified_data, normalized_color)
            elif color_type == 'stroke':
                self._change_stroke_colors(modified_data, normalized_color)
            elif color_type == 'background':
                self._change_background_color(modified_data, normalized_color)
            else:
                # Change all colors
                self._change_fill_colors(modified_data, normalized_color)
                self._change_stroke_colors(modified_data, normalized_color)
            
            print(f"✅ Color change applied successfully")
            return modified_data
            
        except Exception as e:
            print(f"❌ Color change failed: {e}")
            return animation_data
    
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple"""
        try:
            # Remove # if present
            hex_color = hex_color.lstrip('#')
            
            # Handle 3-digit hex
            if len(hex_color) == 3:
                hex_color = ''.join([c*2 for c in hex_color])
            
            # Convert to RGB
            if len(hex_color) == 6:
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                return (r, g, b)
            
            return None
        except Exception as e:
            print(f"Hex to RGB conversion failed: {e}")
            return None
    
    def _change_fill_colors(self, animation_data: Dict[str, Any], color: List[float]):
        """Change fill colors in the animation"""
        try:
            layers = animation_data.get('layers', [])
            for layer in layers:
                shapes = layer.get('shapes', [])
                for shape in shapes:
                    if shape.get('ty') == 'fl':  # Fill shape
                        if 'c' in shape and 'k' in shape['c']:
                            shape['c']['k'] = color
                        elif 'c' in shape:
                            shape['c'] = {'k': color}
                        else:
                            shape['c'] = {'k': color}
        except Exception as e:
            print(f"Fill color change failed: {e}")
    
    def _change_stroke_colors(self, animation_data: Dict[str, Any], color: List[float]):
        """Change stroke colors in the animation"""
        try:
            layers = animation_data.get('layers', [])
            for layer in layers:
                shapes = layer.get('shapes', [])
                for shape in shapes:
                    if shape.get('ty') == 'st':  # Stroke shape
                        if 'c' in shape and 'k' in shape['c']:
                            shape['c']['k'] = color
                        elif 'c' in shape:
                            shape['c'] = {'k': color}
                        else:
                            shape['c'] = {'k': color}
        except Exception as e:
            print(f"Stroke color change failed: {e}")
    
    def _change_background_color(self, animation_data: Dict[str, Any], color: List[float]):
        """Change background color in the animation"""
        try:
            # Look for background layer
            layers = animation_data.get('layers', [])
            for layer in layers:
                if layer.get('ty') == 1:  # Solid layer (background)
                    if 'sc' in layer:
                        layer['sc'] = color
                    else:
                        layer['sc'] = color
                    break
            else:
                # Create a background layer if none exists
                bg_layer = {
                    'ty': 1,  # Solid layer
                    'sc': color,
                    'sw': animation_data.get('w', 400),
                    'sh': animation_data.get('h', 400),
                    'ip': 0,
                    'op': animation_data.get('op', 60),
                    'st': 0,
                    'bm': 0,
                    'sr': 1,
                    'ks': {
                        'o': {'a': 0, 'k': 100},
                        'r': {'a': 0, 'k': 0},
                        'p': {'a': 0, 'k': [0, 0, 0]},
                        'a': {'a': 0, 'k': [0, 0, 0]},
                        's': {'a': 0, 'k': [100, 100, 100]}
                    },
                    'ao': 0,
                    'w': animation_data.get('w', 400),
                    'h': animation_data.get('h', 400),
                    'ip': 0,
                    'op': animation_data.get('op', 60),
                    'st': 0,
                    'bm': 0,
                    'sr': 1,
                    'ks': {
                        'o': {'a': 0, 'k': 100},
                        'r': {'a': 0, 'k': 0},
                        'p': {'a': 0, 'k': [0, 0, 0]},
                        'a': {'a': 0, 'k': [0, 0, 0]},
                        's': {'a': 0, 'k': [100, 100, 100]}
                    },
                    'ao': 0
                }
                layers.insert(0, bg_layer)
        except Exception as e:
            print(f"Background color change failed: {e}")
    
    def get_colors_from_animation(self, animation_data: Dict[str, Any]) -> List[str]:
        """Extract all colors from the animation"""
        colors = []
        try:
            layers = animation_data.get('layers', [])
            for layer in layers:
                shapes = layer.get('shapes', [])
                for shape in shapes:
                    if shape.get('ty') in ['fl', 'st']:  # Fill or stroke
                        if 'c' in shape and 'k' in shape['c']:
                            color_data = shape['c']['k']
                            if isinstance(color_data, list) and len(color_data) >= 3:
                                r = int(color_data[0] * 255)
                                g = int(color_data[1] * 255)
                                b = int(color_data[2] * 255)
                                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                                if hex_color not in colors:
                                    colors.append(hex_color)
        except Exception as e:
            print(f"Color extraction failed: {e}")
        
        return colors

# Global instance
bulletproof_color_changer = BulletproofColorChanger()