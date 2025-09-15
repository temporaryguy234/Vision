"""
LottieFiles Service - Simple fallback implementation
"""
from typing import Dict, Any, List, Optional

class LottieFilesService:
    """Simple LottieFiles service with fallback functionality"""
    
    def __init__(self):
        pass
    
    async def search_animations(
        self, 
        query: Optional[str] = None, 
        category: Optional[str] = None, 
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search animations with fallback"""
        return []
    
    async def get_categories(self) -> List[Dict[str, Any]]:
        """Get categories with fallback"""
        return []
    
    async def get_animation_details(self, animation_id: str) -> Optional[Dict[str, Any]]:
        """Get animation details with fallback"""
        return None
    
    async def download_animation(self, file_url: str) -> Optional[Dict[str, Any]]:
        """Download animation with fallback"""
        return None

# Global instance
lottiefiles_service = LottieFilesService()