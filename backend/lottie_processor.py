import json
import zipfile
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import aiofiles
import aiohttp
from urllib.parse import urlparse

class LottieProcessor:
    """Process and analyze Lottie files to generate manifests"""
    
    def __init__(self):
        self.session = None
    
    async def get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close_session(self):
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def process_file(self, file_path: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Process a Lottie file and return animation data + manifest"""
        try:
            # Extract animation data
            animation_data = await self._extract_animation_data(file_path)
            if not animation_data:
                raise ValueError("Could not extract animation data")
            
            # Generate manifest
            manifest = await self._generate_manifest(animation_data)
            
            return animation_data, manifest
            
        except Exception as e:
            raise ValueError(f"Failed to process Lottie file: {str(e)}")
    
    async def process_url(self, url: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Fetch and process a Lottie file from URL"""
        try:
            # Download file
            session = await self.get_session()
            async with session.get(url) as response:
                if response.status != 200:
                    raise ValueError(f"Failed to fetch URL: {response.status}")
                
                content = await response.read()
                
                # Determine file type from content or URL
                if url.endswith('.lottie') or self._is_zip_content(content):
                    # Process as .lottie ZIP file
                    animation_data = await self._extract_from_zip_content(content)
                else:
                    # Process as JSON
                    animation_data = json.loads(content.decode('utf-8'))
                
                if not animation_data:
                    raise ValueError("Could not extract animation data from URL")
                
                # Generate manifest
                manifest = await self._generate_manifest(animation_data)
                
                return animation_data, manifest
                
        except Exception as e:
            raise ValueError(f"Failed to process URL: {str(e)}")
    
    async def _extract_animation_data(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Extract animation JSON from .json or .lottie file"""
        try:
            if file_path.suffix.lower() == '.lottie':
                # Extract from ZIP
                with zipfile.ZipFile(file_path, 'r') as zip_file:
                    # Look for data.json or main animation file
                    if 'data.json' in zip_file.namelist():
                        with zip_file.open('data.json') as json_file:
                            return json.loads(json_file.read().decode('utf-8'))
                    else:
                        # Find first JSON file
                        json_files = [f for f in zip_file.namelist() if f.endswith('.json')]
                        if json_files:
                            with zip_file.open(json_files[0]) as json_file:
                                return json.loads(json_file.read().decode('utf-8'))
            else:
                # Read JSON file directly
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    return json.loads(content)
            
            return None
            
        except Exception as e:
            print(f"Error extracting animation data: {e}")
            return None
    
    def _is_zip_content(self, content: bytes) -> bool:
        """Check if content is a ZIP file"""
        return content.startswith(b'PK\x03\x04') or content.startswith(b'PK\x05\x06')
    
    async def _extract_from_zip_content(self, content: bytes) -> Optional[Dict[str, Any]]:
        """Extract animation data from ZIP content"""
        try:
            import io
            with zipfile.ZipFile(io.BytesIO(content), 'r') as zip_file:
                if 'data.json' in zip_file.namelist():
                    with zip_file.open('data.json') as json_file:
                        return json.loads(json_file.read().decode('utf-8'))
                else:
                    json_files = [f for f in zip_file.namelist() if f.endswith('.json')]
                    if json_files:
                        with zip_file.open(json_files[0]) as json_file:
                            return json.loads(json_file.read().decode('utf-8'))
            return None
        except Exception as e:
            print(f"Error extracting from ZIP content: {e}")
            return None
    
    async def _generate_manifest(self, animation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate editable elements manifest from animation data"""
        manifest = {
            "text": [],
            "images": [],
            "colors": [],
            "chart": [],
            "speed": {"min": 0.2, "max": 3.0, "default": 1.0},
            "anchors": []
        }
        
        try:
            # Extract basic properties
            width = animation_data.get('w', 1920)
            height = animation_data.get('h', 1080)
            
            # Process layers to find editable elements
            layers = animation_data.get('layers', [])
            await self._process_layers(layers, manifest, width, height)
            
            # Add default anchors for overlays
            manifest["anchors"] = [
                {"id": "top_left", "label": "Top Left", "x": 0.1, "y": 0.1},
                {"id": "top_right", "label": "Top Right", "x": 0.9, "y": 0.1},
                {"id": "bottom_left", "label": "Bottom Left", "x": 0.1, "y": 0.9},
                {"id": "bottom_right", "label": "Bottom Right", "x": 0.9, "y": 0.9},
                {"id": "center", "label": "Center", "x": 0.5, "y": 0.5}
            ]
            
        except Exception as e:
            print(f"Error generating manifest: {e}")
        
        return manifest
    
    async def _process_layers(self, layers: List[Dict], manifest: Dict, width: int, height: int):
        """Process animation layers to identify editable elements"""
        for i, layer in enumerate(layers):
            layer_name = layer.get('nm', f'Layer {i+1}')
            layer_type = layer.get('ty', 0)
            
            # Text layers (ty: 5)
            if layer_type == 5:
                text_data = layer.get('t', {}).get('d', {}).get('k', [])
                if text_data and len(text_data) > 0:
                    text_item = text_data[0] if isinstance(text_data, list) else text_data
                    if isinstance(text_item, dict) and 's' in text_item:
                        manifest["text"].append({
                            "id": f"text_{i}",
                            "label": layer_name,
                            "selector": f"layers[{i}].t.d.k[0].s.t",
                            "default": text_item['s'].get('t', '')
                        })
            
            # Shape layers with fills/strokes (ty: 4)
            elif layer_type == 4:
                shapes = layer.get('shapes', [])
                self._process_shapes(shapes, manifest, i, layer_name)
            
            # Image/video layers (ty: 2)
            elif layer_type == 2:
                ref_id = layer.get('refId', '')
                if ref_id:
                    manifest["images"].append({
                        "id": f"image_{i}",
                        "label": layer_name,
                        "selector": f"assets[refId='{ref_id}'].u",
                        "asset_id": ref_id
                    })
    
    def _process_shapes(self, shapes: List[Dict], manifest: Dict, layer_index: int, layer_name: str):
        """Process shape elements for colors and chart data"""
        for j, shape in enumerate(shapes):
            shape_type = shape.get('ty', '')
            
            # Fill colors
            if shape_type == 'fl':
                color_value = shape.get('c', {}).get('k', [1, 1, 1, 1])
                if isinstance(color_value, list) and len(color_value) >= 3:
                    manifest["colors"].append({
                        "id": f"fill_{layer_index}_{j}",
                        "label": f"{layer_name} Fill",
                        "selector": f"layers[{layer_index}].shapes[{j}].c.k",
                        "default": self._rgba_to_hex(color_value)
                    })
            
            # Stroke colors
            elif shape_type == 'st':
                color_value = shape.get('c', {}).get('k', [0, 0, 0, 1])
                if isinstance(color_value, list) and len(color_value) >= 3:
                    manifest["colors"].append({
                        "id": f"stroke_{layer_index}_{j}",
                        "label": f"{layer_name} Stroke",
                        "selector": f"layers[{layer_index}].shapes[{j}].c.k",
                        "default": self._rgba_to_hex(color_value)
                    })
            
            # Group shapes (recursive)
            elif shape_type == 'gr':
                items = shape.get('it', [])
                if items:
                    self._process_shapes(items, manifest, layer_index, layer_name)
    
    def _rgba_to_hex(self, rgba: List[float]) -> str:
        """Convert RGBA array to hex color"""
        try:
            r = int(rgba[0] * 255)
            g = int(rgba[1] * 255) if len(rgba) > 1 else 0
            b = int(rgba[2] * 255) if len(rgba) > 2 else 0
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return "#000000"

# Global instance
lottie_processor = LottieProcessor()