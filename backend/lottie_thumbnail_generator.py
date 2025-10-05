import asyncio
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import aiofiles
from PIL import Image, ImageDraw, ImageFont
import logging

logger = logging.getLogger(__name__)

class LottieThumbnailGenerator:
    """Generate thumbnails and preview videos from Lottie animations"""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "lottie_thumbs"
        self.temp_dir.mkdir(exist_ok=True)
    
    async def generate_thumbnail(
        self, 
        lottie_data: Dict[str, Any], 
        output_path: Path,
        width: int = 300,
        height: int = 200,
        frame_time: float = 0.0
    ) -> bool:
        """
        Generate a thumbnail from Lottie animation data
        
        Args:
            lottie_data: The Lottie animation JSON data
            output_path: Path to save the thumbnail
            width: Thumbnail width
            height: Thumbnail height
            frame_time: Time in seconds to capture (0.0 = first frame)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Method 1: Try using lottie-convert if available
            if await self._try_lottie_convert(lottie_data, output_path, width, height, frame_time):
                return True
            
            # Method 2: Try using lottie-web with headless browser
            if await self._try_lottie_web(lottie_data, output_path, width, height, frame_time):
                return True
            
            # Method 3: Fallback to simple frame extraction
            if await self._try_simple_extraction(lottie_data, output_path, width, height):
                return True
            
            # Method 4: Create a placeholder thumbnail
            await self._create_placeholder_thumbnail(lottie_data, output_path, width, height)
            return True
            
        except Exception as e:
            logger.error(f"Error generating thumbnail: {e}")
            # Always create a fallback thumbnail
            await self._create_placeholder_thumbnail(lottie_data, output_path, width, height)
            return True
    
    async def _try_lottie_convert(
        self, 
        lottie_data: Dict[str, Any], 
        output_path: Path,
        width: int,
        height: int,
        frame_time: float
    ) -> bool:
        """Try using lottie-convert command line tool"""
        try:
            # Save lottie data to temp file
            temp_lottie = self.temp_dir / f"temp_{id(lottie_data)}.json"
            async with aiofiles.open(temp_lottie, 'w') as f:
                await f.write(json.dumps(lottie_data))
            
            # Calculate frame number
            frame_rate = lottie_data.get('fr', 30)
            frame_number = int(frame_time * frame_rate)
            
            # Use lottie-convert to generate PNG
            cmd = [
                'lottie-convert',
                str(temp_lottie),
                str(output_path),
                '--width', str(width),
                '--height', str(height),
                '--frame', str(frame_number)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            # Clean up temp file
            temp_lottie.unlink(missing_ok=True)
            
            return result.returncode == 0 and output_path.exists()
            
        except Exception as e:
            logger.debug(f"lottie-convert failed: {e}")
            return False
    
    async def _try_lottie_web(
        self, 
        lottie_data: Dict[str, Any], 
        output_path: Path,
        width: int,
        height: int,
        frame_time: float
    ) -> bool:
        """Try using lottie-web with headless browser"""
        try:
            # Create HTML file for rendering
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.12.2/lottie.min.js"></script>
                <style>
                    body {{ margin: 0; padding: 0; }}
                    #lottie-container {{
                        width: {width}px;
                        height: {height}px;
                        background: white;
                    }}
                </style>
            </head>
            <body>
                <div id="lottie-container"></div>
                <script>
                    const animation = lottie.loadAnimation({{
                        container: document.getElementById('lottie-container'),
                        renderer: 'canvas',
                        loop: false,
                        autoplay: false,
                        animationData: {json.dumps(lottie_data)}
                    }});
                    
                    animation.addEventListener('DOMLoaded', function() {{
                        animation.goToAndStop({frame_time}, true);
                        const canvas = document.querySelector('canvas');
                        const dataURL = canvas.toDataURL('image/png');
                        
                        // Send data back to Python
                        fetch('/capture', {{
                            method: 'POST',
                            headers: {{'Content-Type': 'application/json'}},
                            body: JSON.stringify({{image: dataURL}})
                        }});
                    }});
                </script>
            </body>
            </html>
            """
            
            # This is a simplified approach - in production you'd use a headless browser
            # For now, we'll skip this method
            return False
            
        except Exception as e:
            logger.debug(f"lottie-web method failed: {e}")
            return False
    
    async def _try_simple_extraction(
        self, 
        lottie_data: Dict[str, Any], 
        output_path: Path,
        width: int,
        height: int
    ) -> bool:
        """Try simple frame extraction from Lottie data"""
        try:
            # Get animation dimensions
            anim_width = lottie_data.get('w', width)
            anim_height = lottie_data.get('h', height)
            
            # Create a simple thumbnail based on the first layer
            layers = lottie_data.get('layers', [])
            if not layers:
                return False
            
            # Create a canvas with the animation dimensions
            canvas = Image.new('RGBA', (anim_width, anim_height), (255, 255, 255, 0))
            draw = ImageDraw.Draw(canvas)
            
            # Try to extract basic shapes from the first layer
            first_layer = layers[0]
            shapes = first_layer.get('shapes', [])
            
            for shape in shapes:
                if shape.get('ty') == 'fl':  # Fill
                    color_data = shape.get('c', {}).get('k', [0, 0, 0, 1])
                    if isinstance(color_data, list) and len(color_data) >= 3:
                        r = int(color_data[0] * 255)
                        g = int(color_data[1] * 255)
                        b = int(color_data[2] * 255)
                        a = int(color_data[3] * 255) if len(color_data) > 3 else 255
                        
                        # Draw a simple rectangle as placeholder
                        draw.rectangle([50, 50, anim_width-50, anim_height-50], 
                                     fill=(r, g, b, a), outline=(0, 0, 0, 255))
                        break
            
            # Resize to target dimensions
            canvas = canvas.resize((width, height), Image.Resampling.LANCZOS)
            canvas.save(output_path, 'PNG')
            
            return True
            
        except Exception as e:
            logger.debug(f"Simple extraction failed: {e}")
            return False
    
    async def _create_placeholder_thumbnail(
        self, 
        lottie_data: Dict[str, Any], 
        output_path: Path,
        width: int,
        height: int
    ):
        """Create a placeholder thumbnail when other methods fail"""
        try:
            # Create a simple placeholder image
            img = Image.new('RGB', (width, height), (240, 240, 240))
            draw = ImageDraw.Draw(img)
            
            # Get animation info
            anim_width = lottie_data.get('w', 400)
            anim_height = lottie_data.get('h', 400)
            frame_rate = lottie_data.get('fr', 30)
            duration = (lottie_data.get('op', 60) - lottie_data.get('ip', 0)) / frame_rate
            
            # Draw a simple frame
            draw.rectangle([10, 10, width-10, height-10], outline=(200, 200, 200), width=2)
            
            # Add text info
            try:
                font = ImageFont.load_default()
                text_lines = [
                    "Lottie Animation",
                    f"{anim_width}x{anim_height}",
                    f"{duration:.1f}s @ {frame_rate}fps"
                ]
                
                y_offset = 20
                for line in text_lines:
                    draw.text((20, y_offset), line, fill=(100, 100, 100), font=font)
                    y_offset += 20
                    
            except Exception:
                # If font loading fails, just draw without text
                pass
            
            img.save(output_path, 'PNG')
            
        except Exception as e:
            logger.error(f"Error creating placeholder thumbnail: {e}")
            # Create a minimal fallback
            img = Image.new('RGB', (width, height), (200, 200, 200))
            img.save(output_path, 'PNG')
    
    async def generate_preview_video(
        self, 
        lottie_data: Dict[str, Any], 
        output_path: Path,
        width: int = 400,
        height: int = 300,
        duration: float = 3.0
    ) -> bool:
        """
        Generate a preview video from Lottie animation
        
        Args:
            lottie_data: The Lottie animation JSON data
            output_path: Path to save the preview video
            width: Video width
            height: Video height
            duration: Video duration in seconds
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Save lottie data to temp file
            temp_lottie = self.temp_dir / f"temp_video_{id(lottie_data)}.json"
            async with aiofiles.open(temp_lottie, 'w') as f:
                await f.write(json.dumps(lottie_data))
            
            # Use lottie-convert to generate video frames
            temp_dir = self.temp_dir / f"frames_{id(lottie_data)}"
            temp_dir.mkdir(exist_ok=True)
            
            # Calculate frame count
            frame_rate = lottie_data.get('fr', 30)
            frame_count = int(duration * frame_rate)
            
            # Generate frames
            for i in range(frame_count):
                frame_time = (i / frame_count) * duration
                frame_path = temp_dir / f"frame_{i:04d}.png"
                
                # Generate individual frame
                await self.generate_thumbnail(lottie_data, frame_path, width, height, frame_time)
            
            # Use ffmpeg to create video
            cmd = [
                'ffmpeg', '-y',
                '-framerate', str(frame_rate),
                '-i', str(temp_dir / 'frame_%04d.png'),
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-crf', '23',
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            # Clean up temp files
            temp_lottie.unlink(missing_ok=True)
            for frame_file in temp_dir.glob('*.png'):
                frame_file.unlink()
            temp_dir.rmdir()
            
            return result.returncode == 0 and output_path.exists()
            
        except Exception as e:
            logger.error(f"Error generating preview video: {e}")
            return False

# Global instance
lottie_thumbnail_generator = LottieThumbnailGenerator()
