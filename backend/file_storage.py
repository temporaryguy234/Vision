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
        """Extract metadata from Lottie JSON file"""
        try:
            async with aiofiles.open(file_path, 'r') as f:
                content = await f.read()
                data = json.loads(content)
                
                return {
                    'width': data.get('w'),
                    'height': data.get('h'),
                    'duration': (data.get('op', 0) - data.get('ip', 0)) / data.get('fr', 30),
                    'frame_rate': data.get('fr', 30)
                }
        except Exception as e:
            print(f"Error getting Lottie metadata: {e}")
            return {}
    
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
            
            # For other types, we might return a default thumbnail or None
            return None
            
        except Exception as e:
            print(f"Error generating thumbnail: {e}")
            return None

# Global instance
file_storage = FileStorageManager()