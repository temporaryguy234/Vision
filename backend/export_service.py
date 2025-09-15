import os
import asyncio
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
from PIL import Image, ImageDraw, ImageFont
import tempfile
from datetime import datetime
import uuid

class ExportService:
    def __init__(self, db, file_storage):
        self.db = db
        self.file_storage = file_storage
        self.export_dir = Path("/app/exports")
        self.export_dir.mkdir(exist_ok=True, parents=True)
    
    async def export_animation(
        self,
        user_id: str,
        template_id: str,
        current_state: Dict[str, Any],
        export_format: str = "MP4",
        resolution: str = "1080p",
        add_watermark: bool = False
    ) -> Dict[str, Any]:
        """Export animation with current edits"""
        
        try:
            # Get template and animation data
            template = await self.db.templates.find_one({"id": template_id})
            if not template:
                raise Exception("Template not found")
            
            # Load original animation data
            file_url = template.get('file_url', '')
            if not file_url.startswith('/uploads/'):
                raise Exception("Invalid animation file path")
            
            file_path = Path("/app") / file_url[1:]  # Remove leading slash
            if not file_path.exists():
                raise Exception("Animation file not found")
            
            # Load and apply edits
            with open(file_path, 'r') as f:
                animation_data = json.load(f)
            
            # Apply current state to animation data
            modified_animation = self._apply_edits_to_animation(
                animation_data, 
                current_state, 
                template.get('manifest', {})
            )
            
            # Generate export
            export_id = str(uuid.uuid4())
            export_filename = f"{export_id}.{export_format.lower()}"
            export_path = self.export_dir / export_filename
            
            if export_format.upper() == "MP4":
                await self._export_to_mp4(
                    modified_animation, 
                    export_path, 
                    resolution,
                    add_watermark
                )
            elif export_format.upper() == "GIF":
                await self._export_to_gif(
                    modified_animation, 
                    export_path, 
                    resolution,
                    add_watermark
                )
            elif export_format.upper() == "JSON":
                await self._export_to_json(modified_animation, export_path)
            else:
                raise Exception(f"Unsupported export format: {export_format}")
            
            # Create export record
            export_record = {
                "id": export_id,
                "user_id": user_id,
                "template_id": template_id,
                "format": export_format,
                "resolution": resolution,
                "file_path": str(export_path),
                "download_url": f"/exports/{export_filename}",
                "file_size": export_path.stat().st_size if export_path.exists() else 0,
                "has_watermark": add_watermark,
                "status": "completed",
                "created_at": datetime.utcnow()
            }
            
            await self.db.exports.insert_one(export_record)
            
            return {
                "export_id": export_id,
                "download_url": export_record["download_url"],
                "file_size": export_record["file_size"],
                "status": "completed"
            }
            
        except Exception as e:
            # Create failed export record
            export_id = str(uuid.uuid4())
            export_record = {
                "id": export_id,
                "user_id": user_id,
                "template_id": template_id,
                "format": export_format,
                "resolution": resolution,
                "status": "failed",
                "error_message": str(e),
                "created_at": datetime.utcnow()
            }
            
            await self.db.exports.insert_one(export_record)
            
            raise Exception(f"Export failed: {str(e)}")
    
    def _apply_edits_to_animation(
        self, 
        animation_data: Dict[str, Any], 
        current_state: Dict[str, Any], 
        manifest: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply user edits to animation data"""
        modified_data = json.loads(json.dumps(animation_data))  # Deep copy
        
        # Apply text changes
        for text_element in manifest.get('text', []):
            element_id = text_element['id']
            if f"text.{element_id}" in current_state:
                new_text = current_state[f"text.{element_id}"]
                selector = text_element.get('selector', '')
                self._set_by_selector(modified_data, selector, new_text)
        
        # Apply color changes
        for color_element in manifest.get('colors', []):
            element_id = color_element['id']
            if f"colors.{element_id}" in current_state:
                new_color = current_state[f"colors.{element_id}"]
                selector = color_element.get('selector', '')
                # Convert hex to RGBA array for Lottie
                rgba = self._hex_to_rgba_array(new_color)
                self._set_by_selector(modified_data, selector, rgba)
        
        # Apply speed changes
        if 'speed' in current_state:
            speed = current_state['speed']
            # Modify frame rate or animation timing
            if 'fr' in modified_data:
                modified_data['fr'] = int(modified_data['fr'] * speed)
        
        return modified_data
    
    def _set_by_selector(self, obj: Dict[str, Any], selector: str, value: Any) -> bool:
        """Set value using CSS-like selector"""
        try:
            # Parse selector like "layers[0].t.d.k[0].s.t"
            tokens = selector.replace(']', '').split('[')
            tokens = [token.split('.') for token in tokens]
            tokens = [item for sublist in tokens for item in sublist if item]
            
            current = obj
            for i, token in enumerate(tokens[:-1]):
                if token.isdigit():
                    current = current[int(token)]
                else:
                    current = current[token]
            
            # Set final value
            final_key = tokens[-1]
            if final_key.isdigit():
                current[int(final_key)] = value
            else:
                current[final_key] = value
            
            return True
        except:
            return False
    
    def _hex_to_rgba_array(self, hex_color: str) -> List[float]:
        """Convert hex color to RGBA array for Lottie"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            return [1, 1, 1, 1]
        
        try:
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
            return [r, g, b, 1.0]
        except:
            return [1, 1, 1, 1]
    
    async def _export_to_mp4(
        self, 
        animation_data: Dict[str, Any], 
        output_path: Path, 
        resolution: str,
        add_watermark: bool
    ):
        """Export animation to MP4 using lottie-convert or similar"""
        # For now, create a placeholder MP4
        # In production, you'd use tools like lottie-convert, puppeteer, or similar
        
        # Create temporary Lottie file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(animation_data, f)
            temp_lottie_path = f.name
        
        try:
            # Resolution mapping
            resolution_map = {
                "480p": (854, 480),
                "720p": (1280, 720),
                "1080p": (1920, 1080),
                "4K": (3840, 2160)
            }
            
            width, height = resolution_map.get(resolution, (1280, 720))
            
            # For demo purposes, create a simple video file
            # In production, use proper Lottie rendering
            await self._create_demo_video(output_path, width, height, add_watermark)
            
        finally:
            # Clean up temp file
            Path(temp_lottie_path).unlink(missing_ok=True)
    
    async def _export_to_gif(
        self, 
        animation_data: Dict[str, Any], 
        output_path: Path, 
        resolution: str,
        add_watermark: bool
    ):
        """Export animation to GIF"""
        # Create demo GIF
        await self._create_demo_gif(output_path, add_watermark)
    
    async def _export_to_json(self, animation_data: Dict[str, Any], output_path: Path):
        """Export as JSON (Lottie file)"""
        with open(output_path, 'w') as f:
            json.dump(animation_data, f, indent=2)
    
    async def _create_demo_video(self, output_path: Path, width: int, height: int, add_watermark: bool):
        """Create demo video file (placeholder for actual rendering)"""
        # Create a simple colored video using FFmpeg
        duration = 3  # 3 seconds
        
        # Create solid color video
        cmd = [
            'ffmpeg', '-f', 'lavfi', '-i', f'color=c=orange:size={width}x{height}:duration={duration}',
            '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-y', str(output_path)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            
            if add_watermark:
                await self._add_watermark_to_video(output_path)
                
        except subprocess.CalledProcessError:
            # Fallback: create empty file
            output_path.touch()
    
    async def _create_demo_gif(self, output_path: Path, add_watermark: bool):
        """Create demo GIF file"""
        # Create simple animated GIF using PIL
        frames = []
        
        for i in range(30):  # 30 frames
            img = Image.new('RGB', (400, 400), color=(255, 165, 0))  # Orange
            
            if add_watermark:
                self._add_watermark_to_image(img)
            
            frames.append(img)
        
        # Save as GIF
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=100,  # 100ms per frame
            loop=0
        )
    
    async def _add_watermark_to_video(self, video_path: Path):
        """Add watermark to video"""
        temp_path = video_path.with_suffix('.temp.mp4')
        
        cmd = [
            'ffmpeg', '-i', str(video_path),
            '-vf', 'drawtext=text="MotionEdit":fontcolor=white@0.5:fontsize=24:x=10:y=10',
            '-c:a', 'copy', '-y', str(temp_path)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            temp_path.replace(video_path)
        except subprocess.CalledProcessError:
            # If watermark fails, keep original
            temp_path.unlink(missing_ok=True)
    
    def _add_watermark_to_image(self, img: Image.Image):
        """Add watermark to image"""
        draw = ImageDraw.Draw(img)
        
        # Try to use a font, fallback to default
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        # Add watermark text
        draw.text((10, 10), "MotionEdit", fill=(255, 255, 255, 128), font=font)
    
    async def get_user_exports(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get user's export history"""
        cursor = self.db.exports.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
        exports = await cursor.to_list(length=None)
        return exports
    
    async def delete_export(self, export_id: str, user_id: str) -> bool:
        """Delete an export"""
        export_doc = await self.db.exports.find_one({"id": export_id, "user_id": user_id})
        if not export_doc:
            return False
        
        # Delete file
        file_path = export_doc.get('file_path')
        if file_path:
            Path(file_path).unlink(missing_ok=True)
        
        # Delete record
        await self.db.exports.delete_one({"id": export_id})
        return True