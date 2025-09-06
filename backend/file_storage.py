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
        elif extension == '.mp4':
            return AssetType.MP4
        elif extension == '.webm':
            return AssetType.WEBM_ALPHA
        elif extension == '.gif':
            return AssetType.GIF
        elif extension == '.png':
            return AssetType.PNG
        elif extension == '.svg':
            return AssetType.SVG
        # Also check for plain JSON files and validate if they're Lottie
        elif extension == '.json':
            return AssetType.LOTTIE_JSON  # We'll validate in save_uploaded_file
        
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
        """Validate that a JSON file is a valid Lottie animation"""
        try:
            async with aiofiles.open(file_path, 'r') as f:
                content = await f.read()
                data = json.loads(content)
                
                # Basic Lottie validation - check for required fields
                required_fields = ['v', 'fr', 'ip', 'op', 'w', 'h', 'layers']
                return all(field in data for field in required_fields)
        except Exception as e:
            print(f"Error validating Lottie file: {e}")
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
        
        # Save file
        try:
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
                file_size = len(content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
        
        # Get file metadata based on asset type
        metadata = {'file_size': file_size}
        
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