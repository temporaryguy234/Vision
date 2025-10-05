"""
LottieFiles Service - Simple fallback implementation
"""
from typing import Dict, Any, List, Optional

class LottieFilesService:
    """Simple LottieFiles service with fallback functionality"""

    def __init__(self):
        # Minimal mock dataset so the UI has content if no real API is configured
        self._data = [
            {
                "id": "mock_1",
                "name": "Mock Spinner",
                "description": "A simple spinner animation",
                "tags": ["spinner", "loader"],
                "category": "Animated Icons",
                "dimensions": {"width": 200, "height": 200},
                "thumbnail_url": "https://via.placeholder.com/200x200.png?text=Lottie",
                "file_url": "https://assets9.lottiefiles.com/packages/lf20_u4yrau.json"
            },
            {
                "id": "mock_2",
                "name": "Mock Check",
                "description": "Checkmark success animation",
                "tags": ["success", "check"],
                "category": "Animated Icons",
                "dimensions": {"width": 256, "height": 256},
                "thumbnail_url": "https://via.placeholder.com/256x256.png?text=Lottie",
                "file_url": "https://assets6.lottiefiles.com/packages/lf20_jbrw3hcz.json"
            }
        ]

    async def search_animations(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Search animations with fallback"""
        results = self._data
        if query:
            q = query.lower()
            results = [r for r in results if q in r["name"].lower() or q in (r.get("description") or "").lower()]
        if category:
            results = [r for r in results if r.get("category") == category]
        return {"results": results[:limit]}

    async def get_categories(self) -> List[Dict[str, Any]]:
        """Get categories with fallback"""
        cats = sorted(set([item.get("category", "Miscellaneous") for item in self._data]))
        return [{"slug": c.lower().replace(" ", "-"), "name": c} for c in cats]

    async def get_animation_details(self, animation_id: str) -> Optional[Dict[str, Any]]:
        """Get animation details with fallback"""
        for item in self._data:
            if item["id"] == animation_id:
                return item
        return None

    async def download_animation(self, file_url: str) -> Optional[Dict[str, Any]]:
        """Download animation with fallback"""
        try:
            import httpx
            async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
                resp = await client.get(file_url)
                if resp.status_code == 200:
                    return resp.json()
        except Exception:
            pass
        return None

# Global instance
lottiefiles_service = LottieFilesService()