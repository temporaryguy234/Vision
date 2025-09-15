"""
Bulletproof Thumbnail Generator
A robust, self-contained module for generating Lottie thumbnails without external dependencies
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image, ImageDraw, ImageFont
import base64
import io

class BulletproofThumbnailGenerator:
    """A bulletproof thumbnail generator that always works"""
    
    def __init__(self):
        self.default_size = (300, 200)
        self.fallback_colors = [
            (255, 107, 0),   # Orange
            (255, 0, 0),     # Red
            (0, 255, 0),     # Green
            (0, 0, 255),     # Blue
            (128, 0, 128),   # Purple
            (255, 192, 203), # Pink
        ]
    
    def generate_lottie_thumbnail(self, lottie_data: Dict[str, Any], output_path: Path) -> bool:
        """
        Generate a thumbnail for Lottie animation data
        Returns True if successful, False otherwise
        """
        try:
            print(f"🎨 Generating bulletproof thumbnail for Lottie animation")
            
            # Extract basic info from Lottie data
            width = lottie_data.get('w', 400)
            height = lottie_data.get('h', 400)
            frame_rate = lottie_data.get('fr', 30)
            layers_count = len(lottie_data.get('layers', []))
            
            # Calculate duration
            in_point = lottie_data.get('ip', 0)
            out_point = lottie_data.get('op', 60)
            duration = (out_point - in_point) / frame_rate if frame_rate > 0 else 2.0
            
            # Create thumbnail image
            img = Image.new('RGB', self.default_size, (255, 255, 255))
            draw = ImageDraw.Draw(img)
            
            # Draw gradient background
            self._draw_gradient_background(draw)
            
            # Draw frame
            self._draw_frame(draw)
            
            # Extract and draw colors from animation
            colors = self._extract_colors_from_lottie(lottie_data)
            self._draw_color_swatches(draw, colors)
            
            # Draw animation info
            self._draw_animation_info(draw, width, height, duration, frame_rate, layers_count)
            
            # Draw Lottie icon
            self._draw_lottie_icon(draw)
            
            # Save thumbnail
            img.save(output_path, 'PNG')
            print(f"✅ Bulletproof thumbnail saved: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Bulletproof thumbnail generation failed: {e}")
            
            # Ultimate fallback - create a simple colored rectangle
            try:
                self._create_ultimate_fallback(output_path)
                return True
            except Exception as fallback_error:
                print(f"❌ Ultimate fallback also failed: {fallback_error}")
                return False
    
    def _draw_gradient_background(self, draw: ImageDraw.Draw):
        """Draw a subtle gradient background"""
        for y in range(self.default_size[1]):
            color_value = int(240 - (y * 0.1))
            draw.line([(0, y), (self.default_size[0], y)], fill=(color_value, color_value, color_value))
    
    def _draw_frame(self, draw: ImageDraw.Draw):
        """Draw a decorative frame"""
        # Outer frame
        draw.rectangle([5, 5, self.default_size[0]-5, self.default_size[1]-5], 
                      outline=(200, 200, 200), width=2)
        # Inner frame
        draw.rectangle([10, 10, self.default_size[0]-10, self.default_size[1]-10], 
                      outline=(220, 220, 220), width=1)
    
    def _extract_colors_from_lottie(self, lottie_data: Dict[str, Any]) -> list:
        """Extract colors from Lottie animation data"""
        colors = []
        
        try:
            layers = lottie_data.get('layers', [])
            for layer in layers[:5]:  # Check first 5 layers
                shapes = layer.get('shapes', [])
                for shape in shapes:
                    if shape.get('ty') == 'fl':  # Fill
                        color_data = shape.get('c', {}).get('k', [0, 0, 0, 1])
                        if isinstance(color_data, list) and len(color_data) >= 3:
                            r = int(color_data[0] * 255)
                            g = int(color_data[1] * 255)
                            b = int(color_data[2] * 255)
                            colors.append((r, g, b))
                            if len(colors) >= 4:
                                break
                    elif shape.get('ty') == 'st':  # Stroke
                        color_data = shape.get('c', {}).get('k', [0, 0, 0, 1])
                        if isinstance(color_data, list) and len(color_data) >= 3:
                            r = int(color_data[0] * 255)
                            g = int(color_data[1] * 255)
                            b = int(color_data[2] * 255)
                            colors.append((r, g, b))
                            if len(colors) >= 4:
                                break
                if len(colors) >= 4:
                    break
        except Exception as e:
            print(f"Color extraction failed: {e}")
        
        # Use fallback colors if none found
        if not colors:
            colors = self.fallback_colors[:3]
        
        return colors[:4]  # Max 4 colors
    
    def _draw_color_swatches(self, draw: ImageDraw.Draw, colors: list):
        """Draw color swatches"""
        if not colors:
            return
        
        swatch_size = 30
        start_x = 20
        start_y = 40
        
        for i, color in enumerate(colors[:4]):
            x = start_x + (i * (swatch_size + 10))
            y = start_y
            
            # Draw color swatch
            draw.rectangle([x, y, x + swatch_size, y + swatch_size], 
                          fill=color, outline=(100, 100, 100))
            
            # Draw small border
            draw.rectangle([x+2, y+2, x + swatch_size-2, y + swatch_size-2], 
                          outline=(255, 255, 255), width=1)
    
    def _draw_animation_info(self, draw: ImageDraw.Draw, width: int, height: int, 
                           duration: float, frame_rate: int, layers_count: int):
        """Draw animation information text"""
        try:
            # Try to load a font
            try:
                font = ImageFont.truetype("arial.ttf", 12)
            except:
                try:
                    font = ImageFont.load_default()
                except:
                    font = None
            
            # Animation info text
            info_lines = [
                f"Lottie Animation",
                f"{width}×{height}",
                f"{duration:.1f}s @ {frame_rate}fps",
                f"{layers_count} layers"
            ]
            
            y_offset = 90
            for line in info_lines:
                if font:
                    # Center the text
                    bbox = draw.textbbox((0, 0), line, font=font)
                    text_width = bbox[2] - bbox[0]
                    x = (self.default_size[0] - text_width) // 2
                else:
                    x = 20
                
                draw.text((x, y_offset), line, fill=(80, 80, 80), font=font)
                y_offset += 18
                
        except Exception as e:
            print(f"Text drawing failed: {e}")
    
    def _draw_lottie_icon(self, draw: ImageDraw.Draw):
        """Draw a simple Lottie icon"""
        try:
            # Draw a simple "L" icon
            icon_x = self.default_size[0] - 40
            icon_y = 20
            icon_size = 20
            
            # Draw "L" shape
            draw.rectangle([icon_x, icon_y, icon_x + 3, icon_y + icon_size], 
                          fill=(255, 107, 0))  # Orange
            draw.rectangle([icon_x, icon_y + icon_size - 3, icon_x + icon_size, icon_y + icon_size], 
                          fill=(255, 107, 0))  # Orange
        except Exception as e:
            print(f"Icon drawing failed: {e}")
    
    def _create_ultimate_fallback(self, output_path: Path):
        """Create the most basic fallback thumbnail"""
        img = Image.new('RGB', self.default_size, (240, 240, 240))
        draw = ImageDraw.Draw(img)
        
        # Draw a simple rectangle
        draw.rectangle([20, 20, self.default_size[0]-20, self.default_size[1]-20], 
                      fill=(255, 107, 0), outline=(200, 200, 200), width=2)
        
        # Draw "LOTTIE" text
        try:
            font = ImageFont.load_default()
            text = "LOTTIE"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (self.default_size[0] - text_width) // 2
            y = (self.default_size[1] - text_height) // 2
            draw.text((x, y), text, fill=(255, 255, 255), font=font)
        except:
            pass
        
        img.save(output_path, 'PNG')
        print(f"✅ Ultimate fallback thumbnail created: {output_path}")

# Global instance
bulletproof_thumbnail_generator = BulletproofThumbnailGenerator()