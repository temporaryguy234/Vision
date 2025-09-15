import os
import uuid
import mimetypes
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import asyncio
import aiofiles
from fastapi import UploadFile, HTTPException
import json
import subprocess
from PIL import Image
from models import AssetType

class FileStorageManager:
    def __init__(self, base_upload_dir: str = "/app/uploads"):
        self.base_upload_dir = Path(base_upload_dir)
        self.base_upload_dir.mkdir(exist_ok=True, parents=True)
        
        # Create subdirectories for different asset types
        self.subdirs = {
            AssetType.LOTTIE_JSON: self.base_upload_dir / "lottie",
            AssetType.MP4: self.base_upload_dir / "videos" / "mp4",
            AssetType.WEBM_ALPHA: self.base_upload_dir / "videos" / "webm",
            AssetType.GIF: self.base_upload_dir / "images" / "gif",
            AssetType.PNG: self.base_upload_dir / "images" / "png",
            AssetType.SVG: self.base_upload_dir / "images" / "svg",
        }
        
        for subdir in self.subdirs.values():
            subdir.mkdir(exist_ok=True, parents=True)
    
    def _get_asset_type_from_file(self, filename: str, content_type: str) -> Optional[AssetType]:
        """Determine asset type from filename and content type"""
        extension = Path(filename).suffix.lower()
        filename_lower = filename.lower()
        
        # Check for Lottie JSON files - can be .json or .lottie extensions
        if (extension == '.json' and ('lottie' in filename_lower or 'bodymovin' in filename_lower)) or extension == '.lottie':
            return AssetType.LOTTIE_JSON
        elif extension in ['.mp4', '.mov', '.avi']:
            return AssetType.MP4
        elif extension == '.webm':
            return AssetType.WEBM_ALPHA
        elif extension in ['.gif', '.apng']:
            return AssetType.GIF
        elif extension in ['.png', '.jpg', '.jpeg']:
            return AssetType.PNG
        elif extension == '.svg':
            return AssetType.SVG
        # Also check for plain JSON files and validate if they're Lottie
        elif extension == '.json':
            return AssetType.LOTTIE_JSON  # We'll validate in save_uploaded_file
        # Project files - treat as generic assets for now
        elif extension in ['.aep', '.prproj', '.blend', '.c4d']:
            return AssetType.PNG  # Store as generic asset
        
        return None
    
    def _generate_unique_filename(self, original_filename: str) -> str:
        """Generate a unique filename while preserving the extension"""
        extension = Path(original_filename).suffix
        unique_id = str(uuid.uuid4())
        return f"{unique_id}{extension}"
    
    async def _get_image_dimensions(self, file_path: Path) -> Tuple[Optional[int], Optional[int]]:
        """Get image dimensions for PNG/GIF files"""
        try:
            with Image.open(file_path) as img:
                return img.width, img.height
        except Exception as e:
            print(f"Error getting image dimensions: {e}")
            return None, None
    
    async def _get_video_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Get video metadata using ffprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams',
                '-show_format', str(file_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return {}
            
            metadata = json.loads(result.stdout)
            video_stream = None
            
            # Find the video stream
            for stream in metadata.get('streams', []):
                if stream.get('codec_type') == 'video':
                    video_stream = stream
                    break
            
            if not video_stream:
                return {}
            
            return {
                'width': video_stream.get('width'),
                'height': video_stream.get('height'),
                'duration': float(metadata.get('format', {}).get('duration', 0)),
                'frame_rate': self._parse_frame_rate(video_stream.get('r_frame_rate', '30/1'))
            }
        except Exception as e:
            print(f"Error getting video metadata: {e}")
            return {}
    
    def _parse_frame_rate(self, frame_rate_str: str) -> int:
        """Parse frame rate from ffprobe format (e.g., '30/1' -> 30)"""
        try:
            if '/' in frame_rate_str:
                numerator, denominator = frame_rate_str.split('/')
                return int(float(numerator) / float(denominator))
            return int(float(frame_rate_str))
        except:
            return 30  # Default frame rate
    
    async def _validate_lottie_file(self, file_path: Path) -> bool:
        """Validate if a file is a valid Lottie JSON file"""
        try:
            import zipfile
            
            # Check if it's a .lottie file (ZIP format)
            if file_path.suffix.lower() == '.lottie':
                try:
                    with zipfile.ZipFile(file_path, 'r') as zip_file:
                        # Look for data.json in the ZIP
                        if 'data.json' in zip_file.namelist():
                            with zip_file.open('data.json') as json_file:
                                content = json_file.read().decode('utf-8')
                                data = json.loads(content)
                        else:
                            # Some .lottie files might have the JSON at root level
                            json_files = [f for f in zip_file.namelist() if f.endswith('.json')]
                            if json_files:
                                with zip_file.open(json_files[0]) as json_file:
                                    content = json_file.read().decode('utf-8')
                                    data = json.loads(content)
                            else:
                                return False
                except zipfile.BadZipFile:
                    # If it's not a valid ZIP, treat as regular JSON
                    async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                        content = await f.read()
                        data = json.loads(content)
            else:
                # Regular JSON file
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    data = json.loads(content)
            
            # More lenient validation - just check for basic Lottie structure
            if isinstance(data, dict):
                # Check for common Lottie fields (more flexible)
                has_version = 'v' in data or 'version' in data
                has_frame_rate = 'fr' in data or 'frameRate' in data or 'frame_rate' in data
                has_layers = 'layers' in data
                has_dimensions = ('w' in data and 'h' in data) or ('width' in data and 'height' in data)
                
                # If it has most Lottie characteristics, accept it
                lottie_indicators = sum([has_version, has_frame_rate, has_layers, has_dimensions])
                
                if lottie_indicators >= 2:  # More lenient - need at least 2 indicators
                    return True
                
                # Also accept if it's clearly a JSON animation file
                has_animation_terms = any(term in str(data).lower() for term in [
                    'animation', 'keyframe', 'timeline', 'bodymovin', 'lottie', 'after effects'
                ])
                
                if has_animation_terms:
                    return True
                
                # Very lenient: if it has layers and any dimensional info, accept it
                if 'layers' in data and (has_dimensions or has_version):
                    return True
            
            return False
            
        except (json.JSONDecodeError, UnicodeDecodeError, zipfile.BadZipFile, Exception) as e:
            # Very lenient fallback: if filename suggests it's a Lottie file, accept it
            filename_lower = file_path.name.lower()
            if any(term in filename_lower for term in ['lottie', 'bodymovin', 'after_effects', 'animation']):
                return True
            
            return False
    
    async def _get_lottie_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from Lottie JSON file or .lottie ZIP file"""
        try:
            import zipfile
            
            data = None
            
            # Check if it's a .lottie file (ZIP format)
            if file_path.suffix.lower() == '.lottie':
                try:
                    with zipfile.ZipFile(file_path, 'r') as zip_file:
                        # Look for data.json in the ZIP
                        if 'data.json' in zip_file.namelist():
                            with zip_file.open('data.json') as json_file:
                                content = json_file.read().decode('utf-8')
                                data = json.loads(content)
                        else:
                            # Some .lottie files might have the JSON at root level
                            json_files = [f for f in zip_file.namelist() if f.endswith('.json')]
                            if json_files:
                                with zip_file.open(json_files[0]) as json_file:
                                    content = json_file.read().decode('utf-8')
                                    data = json.loads(content)
                except zipfile.BadZipFile:
                    # If it's not a valid ZIP, treat as regular JSON
                    async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                        content = await f.read()
                        data = json.loads(content)
            else:
                # Regular JSON file
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    data = json.loads(content)
            
            if not data:
                return {}
            
            metadata = {}
            
            # Extract basic dimensions
            width = data.get('w') or data.get('width', 400)
            height = data.get('h') or data.get('height', 400)
            metadata['width'] = int(width) if width else 400
            metadata['height'] = int(height) if height else 400
            
            # Extract frame rate and calculate duration
            frame_rate = data.get('fr') or data.get('frameRate') or data.get('frame_rate', 30)
            metadata['frame_rate'] = int(frame_rate) if frame_rate else 30
            
            # Calculate duration from in_point, out_point, and frame rate
            in_point = data.get('ip', 0)
            out_point = data.get('op') or data.get('outPoint', 60)
            
            if out_point and frame_rate:
                duration_frames = float(out_point) - float(in_point)
                duration_seconds = duration_frames / float(frame_rate)
                metadata['duration'] = round(duration_seconds, 2)
            else:
                metadata['duration'] = 2.0  # Default duration
            
            return metadata
            
        except Exception as e:
            print(f"Error extracting Lottie metadata: {e}")
            # Return safe defaults
            return {
                'width': 400,
                'height': 400,
                'frame_rate': 30,
                'duration': 2.0
            }
    
    async def save_uploaded_file(
        self, 
        file: UploadFile, 
        template_id: Optional[str] = None
    ) -> Tuple[str, AssetType, Dict[str, Any]]:
        """
        Save uploaded file and return file URL, asset type, and metadata
        
        Returns:
            Tuple of (file_url, asset_type, metadata)
        """
        import hashlib
        
        # Determine asset type
        asset_type = self._get_asset_type_from_file(file.filename, file.content_type)
        if not asset_type:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file.filename}"
            )
        
        # Generate unique filename
        unique_filename = self._generate_unique_filename(file.filename)
        
        # Determine save directory
        save_dir = self.subdirs[asset_type]
        if template_id:
            save_dir = save_dir / template_id
            save_dir.mkdir(exist_ok=True, parents=True)
        
        file_path = save_dir / unique_filename
        
        # Save file and calculate hash
        try:
            content = await file.read()
            file_size = len(content)
            file_hash = hashlib.md5(content).hexdigest()
            
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
        
        # Get file metadata based on asset type
        metadata = {'file_size': file_size, 'file_hash': file_hash}
        
        if asset_type == AssetType.LOTTIE_JSON:
            # Validate Lottie file
            if not await self._validate_lottie_file(file_path):
                # Clean up invalid file
                file_path.unlink()
                raise HTTPException(status_code=400, detail="Invalid Lottie JSON file")
            
            lottie_metadata = await self._get_lottie_metadata(file_path)
            metadata.update(lottie_metadata)
        
        elif asset_type in [AssetType.MP4, AssetType.WEBM_ALPHA]:
            video_metadata = await self._get_video_metadata(file_path)
            metadata.update(video_metadata)
        
        elif asset_type in [AssetType.PNG, AssetType.GIF]:
            width, height = await self._get_image_dimensions(file_path)
            if width and height:
                metadata.update({'width': width, 'height': height})
        
        elif asset_type == AssetType.SVG:
            # For SVG, we'll set default dimensions (can be overridden)
            metadata.update({'width': 100, 'height': 100})
        
        # Generate public URL (in production, this would be a CDN URL)
        # For now, we'll use a relative path that can be served by the app
        relative_path = file_path.relative_to(self.base_upload_dir)
        file_url = f"/uploads/{relative_path}"
        
        return file_url, asset_type, metadata
    
    async def delete_file(self, file_url: str) -> bool:
        """Delete a file by its URL"""
        try:
            # Extract relative path from URL
            if file_url.startswith("/uploads/"):
                relative_path = file_url[9:]  # Remove "/uploads/"
                file_path = self.base_upload_dir / relative_path
                
                if file_path.exists():
                    file_path.unlink()
                    return True
            return False
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def get_file_path(self, file_url: str) -> Optional[Path]:
        """Get the local file path from a file URL"""
        try:
            if file_url.startswith("/uploads/"):
                relative_path = file_url[9:]  # Remove "/uploads/"
                file_path = self.base_upload_dir / relative_path
                
                if file_path.exists():
                    return file_path
            return None
        except Exception:
            return None
    
    async def generate_thumbnail(self, file_url: str, asset_type: AssetType) -> Optional[str]:
        """Generate a thumbnail for the asset"""
        file_path = self.get_file_path(file_url)
        if not file_path:
            return None
        
        thumbnail_dir = self.base_upload_dir / "thumbnails"
        thumbnail_dir.mkdir(exist_ok=True)
        
        # Generate thumbnail filename
        thumbnail_filename = f"{file_path.stem}_thumb.png"
        thumbnail_path = thumbnail_dir / thumbnail_filename
        
        try:
            if asset_type in [AssetType.MP4, AssetType.WEBM_ALPHA]:
                # Generate video thumbnail using ffmpeg
                cmd = [
                    'ffmpeg', '-i', str(file_path), '-ss', '00:00:01.000',
                    '-vframes', '1', '-y', str(thumbnail_path)
                ]
                result = subprocess.run(cmd, capture_output=True)
                
                if result.returncode == 0 and thumbnail_path.exists():
                    return f"/uploads/thumbnails/{thumbnail_filename}"
            
            elif asset_type in [AssetType.PNG, AssetType.GIF]:
                # For images, create a smaller version
                with Image.open(file_path) as img:
                    # Convert to RGB if necessary
                    if img.mode in ['RGBA', 'P']:
                        img = img.convert('RGB')
                    
                    # Create thumbnail
                    img.thumbnail((300, 200), Image.Resampling.LANCZOS)
                    img.save(thumbnail_path, "PNG")
                    
                    return f"/uploads/thumbnails/{thumbnail_filename}"
            
            # For Lottie JSON, generate a real thumbnail
            if asset_type == AssetType.LOTTIE_JSON:
                return await self._generate_lottie_thumbnail(file_path, thumbnail_path)
            # For other types, we might return a default thumbnail or None
            return None
            
        except Exception as e:
            print(f"Error generating thumbnail: {e}")
            return None

    async def _generate_lottie_thumbnail(self, file_path: Path, thumbnail_path: Path) -> Optional[str]:
        """Generate a thumbnail for Lottie animation using lottie-web"""
        try:
            # Read the Lottie JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                animation_data = json.load(f)
            
            # Create a simple HTML file to render the Lottie animation
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <script src="https://unpkg.com/lottie-web@5.12.2/build/player/lottie.min.js"></script>
            </head>
            <body>
                <div id="lottie-container" style="width: 300px; height: 200px;"></div>
                <script>
                    const animation = lottie.loadAnimation({{
                        container: document.getElementById('lottie-container'),
                        renderer: 'canvas',
                        loop: false,
                        autoplay: false,
                        animationData: {json.dumps(animation_data)}
                    }});
                    
                    animation.addEventListener('DOMLoaded', () => {{
                        // Wait a bit for the animation to render
                        setTimeout(() => {{
                            const canvas = document.querySelector('canvas');
                            if (canvas) {{
                                // Convert canvas to image and send to parent
                                const dataURL = canvas.toDataURL('image/png');
                                window.parent.postMessage({{type: 'thumbnail', data: dataURL}}, '*');
                            }}
                        }}, 100);
                    }});
                </script>
            </body>
            </html>
            """
            
            # For now, create a simple colored thumbnail based on animation properties
            # This is a fallback until we implement proper Lottie rendering
            width = animation_data.get('w', 1920)
            height = animation_data.get('h', 1080)
            
            # Create a simple thumbnail with animation info
            img = Image.new('RGB', (300, 200), color='#f0f0f0')
            
            # Try to get a color from the animation
            bg_color = self._extract_background_color(animation_data)
            if bg_color:
                img = Image.new('RGB', (300, 200), color=bg_color)
            
            # Add some text overlay
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(img)
            
            try:
                # Try to use a default font
                font = ImageFont.load_default()
            except:
                font = None
            
            # Draw animation info
            text_lines = [
                f"Lottie Animation",
                f"{width}x{height}",
                f"{len(animation_data.get('layers', []))} layers"
            ]
            
            y_offset = 50
            for line in text_lines:
                draw.text((10, y_offset), line, fill='#333333', font=font)
                y_offset += 25
            
            # Save thumbnail
            img.save(thumbnail_path, "PNG")
            return f"/uploads/thumbnails/{thumbnail_path.name}"
            
        except Exception as e:
            print(f"Error generating Lottie thumbnail: {e}")
            # Return placeholder as fallback
            return "/uploads/thumbnails/lottie_placeholder.svg"
    
    def _extract_background_color(self, animation_data: Dict) -> Optional[str]:
        """Extract background color from Lottie animation data"""
        try:
            # Look for background color in layers
            layers = animation_data.get('layers', [])
            for layer in layers:
                if layer.get('ty') == 1:  # Solid layer
                    sc = layer.get('sc', '')
                    if sc:
                        # Convert color to hex
                        if isinstance(sc, str) and sc.startswith('#'):
                            return sc
                        elif isinstance(sc, list) and len(sc) >= 3:
                            r, g, b = int(sc[0] * 255), int(sc[1] * 255), int(sc[2] * 255)
                            return f"#{r:02x}{g:02x}{b:02x}"
            
            # Look for background in composition
            bg_color = animation_data.get('bg')
            if bg_color:
                if isinstance(bg_color, str) and bg_color.startswith('#'):
                    return bg_color
                elif isinstance(bg_color, list) and len(bg_color) >= 3:
                    r, g, b = int(bg_color[0] * 255), int(bg_color[1] * 255), int(bg_color[2] * 255)
                    return f"#{r:02x}{g:02x}{b:02x}"
            
            return None
        except:
            return None

    async def generate_preview_video(self, file_url: str, asset_type: AssetType) -> Optional[str]:
        """Generate a preview video for the asset"""
        file_path = self.get_file_path(file_url)
        if not file_path:
            return None
        
        preview_dir = self.base_upload_dir / "previews"
        preview_dir.mkdir(exist_ok=True)
        
        # Generate preview video filename
        preview_filename = f"{file_path.stem}_preview.webm"
        preview_path = preview_dir / preview_filename
        
        try:
            if asset_type == AssetType.LOTTIE_JSON:
                return await self._generate_lottie_preview_video(file_path, preview_path)
            elif asset_type in [AssetType.MP4, AssetType.WEBM_ALPHA]:
                # For video files, create a shorter preview
                cmd = [
                    'ffmpeg', '-i', str(file_path), '-t', '3', '-c:v', 'libvpx-vp9',
                    '-crf', '30', '-b:v', '0', '-y', str(preview_path)
                ]
                result = subprocess.run(cmd, capture_output=True)
                
                if result.returncode == 0 and preview_path.exists():
                    return f"/uploads/previews/{preview_filename}"
            
            return None
            
        except Exception as e:
            print(f"Error generating preview video: {e}")
            return None

    async def _generate_lottie_preview_video(self, file_path: Path, preview_path: Path) -> Optional[str]:
        """Generate a preview video for Lottie animation"""
        try:
            # Read the Lottie JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                animation_data = json.load(f)
            
            # Get animation duration
            duration = animation_data.get('op', 0) / animation_data.get('fr', 30)  # frames / fps
            duration = min(duration, 5)  # Max 5 seconds for preview
            
            # Create a simple HTML file to render the Lottie animation
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <script src="https://unpkg.com/lottie-web@5.12.2/build/player/lottie.min.js"></script>
            </head>
            <body>
                <div id="lottie-container" style="width: 640px; height: 360px;"></div>
                <script>
                    const animation = lottie.loadAnimation({{
                        container: document.getElementById('lottie-container'),
                        renderer: 'canvas',
                        loop: false,
                        autoplay: true,
                        animationData: {json.dumps(animation_data)}
                    }});
                    
                    animation.addEventListener('DOMLoaded', () => {{
                        // Animation is ready
                        console.log('Animation loaded');
                    }});
                </script>
            </body>
            </html>
            """
            
            # For now, return empty string as we need a proper headless browser solution
            # This would require puppeteer or similar to render the HTML and record it
            print(f"Preview video generation for Lottie not fully implemented yet: {file_path}")
            return ""
            
        except Exception as e:
            print(f"Error generating Lottie preview video: {e}")
            return ""

# Global instance
file_storage = FileStorageManager()