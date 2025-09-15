"""
Lottie Processor - Simple fallback implementation
"""
import json
import httpx
from pathlib import Path
from typing import Dict, Any, Tuple

class LottieProcessor:
    """Simple Lottie processor with fallback functionality"""
    
    def __init__(self):
        pass
    
    async def process_file(self, file_path: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Process a Lottie file from local path"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                animation_data = json.load(f)
            
            manifest = self._generate_manifest(animation_data)
            return animation_data, manifest
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            return {}, {}
    
    async def process_url(self, url: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Process a Lottie file from URL"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30.0)
                response.raise_for_status()
                animation_data = response.json()
            
            manifest = self._generate_manifest(animation_data)
            return animation_data, manifest
        except Exception as e:
            print(f"Error processing URL {url}: {e}")
            return {}, {}
    
    def _generate_manifest(self, animation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a simple manifest from animation data"""
        return {
            "canvas": {
                "width": animation_data.get('w', 400),
                "height": animation_data.get('h', 400),
                "background_color": "#FFFFFF",
                "global_playback_speed": 1.0
            },
            "elements": []
        }

# Global instance
lottie_processor = LottieProcessor()