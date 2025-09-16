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
        """Process a Lottie file from local path (.json or .lottie)"""
        try:
            animation_data: Dict[str, Any] = {}
            if file_path.suffix.lower() == '.lottie':
                import zipfile
                try:
                    with zipfile.ZipFile(file_path, 'r') as zip_file:
                        # Prefer data.json
                        if 'data.json' in zip_file.namelist():
                            with zip_file.open('data.json') as json_file:
                                animation_data = json.loads(json_file.read().decode('utf-8'))
                        else:
                            json_files = [f for f in zip_file.namelist() if f.endswith('.json')]
                            if json_files:
                                with zip_file.open(json_files[0]) as json_file:
                                    animation_data = json.loads(json_file.read().decode('utf-8'))
                except zipfile.BadZipFile:
                    # Fall back to reading as JSON
                    with open(file_path, 'r', encoding='utf-8') as f:
                        animation_data = json.load(f)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    animation_data = json.load(f)

            manifest = self._generate_manifest(animation_data)
            return animation_data, manifest
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            return {}, {}
    
    async def process_url(self, url: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Process a Lottie file from URL with robust fetching and parsing"""
        try:
            headers = {
                "User-Agent": "MotionEdit/1.0 (+https://example.com)",
                "Accept": "application/json, text/plain;q=0.9, */*;q=0.8",
            }
            timeout = httpx.Timeout(30.0, connect=15.0)
            async with httpx.AsyncClient(timeout=timeout, follow_redirects=True, headers=headers) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                # Try strict JSON first
                try:
                    animation_data = resp.json()
                except Exception:
                    # Some hosts return text/plain JSON
                    import json as _json
                    animation_data = _json.loads(resp.text)

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