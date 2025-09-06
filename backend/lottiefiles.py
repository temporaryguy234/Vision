import os
import logging
import aiohttp
import asyncio
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class LottieFilesConfig:
    """Configuration for LottieFiles API integration."""
    def __init__(self):
        # For demo purposes, we'll use public animations that don't require API keys
        self.base_url = "https://assets.lottiefiles.com/packages"
        self.public_animations_url = "https://lottiefiles.com/featured"
        self.timeout = 30

class AnimationMetadata(BaseModel):
    """Metadata for a LottieFiles animation."""
    id: str
    name: str
    description: Optional[str] = ""
    tags: List[str] = []
    category: str = "miscellaneous"
    duration: float = 0.0
    file_url: str
    preview_url: str = ""
    thumbnail_url: str = ""
    file_size: int = 0
    dimensions: Dict[str, int] = {"width": 400, "height": 400}

class LottieFilesService:
    """Service for browsing and importing LottieFiles animations."""
    
    def __init__(self):
        self.config = LottieFilesConfig()
        self.logger = logging.getLogger(__name__)
        self._session: Optional[aiohttp.ClientSession] = None
        
        # Curated list of working Lottie animations with embedded JSON data
        self.curated_animations = [
            {
                "id": "loading_spinner",
                "name": "Loading Spinner",
                "description": "Elegant loading animation",
                "category": "loading",
                "tags": ["loading", "spinner", "progress"],
                "file_url": "embedded://loading_spinner",
                "thumbnail_url": "https://assets5.lottiefiles.com/packages/lf20_t9gkkhz4.json",
                "duration": 2.0,
                "dimensions": {"width": 400, "height": 400},
                "lottie_data": {
                    "v": "5.7.4",
                    "fr": 30,
                    "ip": 0,
                    "op": 60,
                    "w": 400,
                    "h": 400,
                    "nm": "Loading Spinner",
                    "ddd": 0,
                    "assets": [],
                    "layers": [
                        {
                            "ddd": 0,
                            "ind": 1,
                            "ty": 4,
                            "nm": "Spinner",
                            "sr": 1,
                            "ks": {
                                "o": {"a": 0, "k": 100},
                                "r": {"a": 1, "k": [
                                    {"i": {"x": [0.833], "y": [0.833]}, "o": {"x": [0.167], "y": [0.167]}, "t": 0, "s": [0]}, 
                                    {"t": 59, "s": [360]}
                                ]},
                                "p": {"a": 0, "k": [200, 200, 0]},
                                "a": {"a": 0, "k": [0, 0, 0]},
                                "s": {"a": 0, "k": [100, 100, 100]}
                            },
                            "ao": 0,
                            "shapes": [
                                {
                                    "ty": "gr",
                                    "it": [
                                        {
                                            "ty": "el",
                                            "p": {"a": 0, "k": [0, 0]},
                                            "s": {"a": 0, "k": [100, 100]}
                                        },
                                        {
                                            "ty": "st",
                                            "c": {"a": 0, "k": [1, 0.5, 0, 1]},
                                            "o": {"a": 0, "k": 100},
                                            "w": {"a": 0, "k": 8}
                                        },
                                        {
                                            "ty": "tr",
                                            "p": {"a": 0, "k": [0, 0]},
                                            "a": {"a": 0, "k": [0, 0]},
                                            "s": {"a": 0, "k": [100, 100]},
                                            "r": {"a": 0, "k": 0},
                                            "o": {"a": 0, "k": 100},
                                            "sk": {"a": 0, "k": 0},
                                            "sa": {"a": 0, "k": 0}
                                        }
                                    ]
                                }
                            ],
                            "ip": 0,
                            "op": 60,
                            "st": 0,
                            "bm": 0
                        }
                    ]
                }
            },
            {
                "id": "success_checkmark",
                "name": "Success Checkmark",
                "description": "Animated success confirmation",
                "category": "success",
                "tags": ["success", "check", "done", "complete"],
                "file_url": "embedded://success_checkmark",
                "thumbnail_url": "https://assets9.lottiefiles.com/packages/lf20_jbrw3hcz.json",
                "duration": 1.5,
                "dimensions": {"width": 400, "height": 400},
                "lottie_data": {
                    "v": "5.7.4",
                    "fr": 30,
                    "ip": 0,
                    "op": 45,
                    "w": 400,
                    "h": 400,
                    "nm": "Success Check",
                    "ddd": 0,
                    "assets": [],
                    "layers": [
                        {
                            "ddd": 0,
                            "ind": 1,
                            "ty": 4,
                            "nm": "Check",
                            "sr": 1,
                            "ks": {
                                "o": {"a": 0, "k": 100},
                                "r": {"a": 0, "k": 0},
                                "p": {"a": 0, "k": [200, 200, 0]},
                                "a": {"a": 0, "k": [0, 0, 0]},
                                "s": {"a": 1, "k": [{"t": 0, "s": [0, 0, 100]}, {"t": 30, "s": [120, 120, 100]}]}
                            },
                            "ao": 0,
                            "shapes": [
                                {
                                    "ty": "gr",
                                    "it": [
                                        {
                                            "ty": "sh",
                                            "ks": {
                                                "a": 0,
                                                "k": {
                                                    "i": [[0,0],[0,0],[0,0]],
                                                    "o": [[0,0],[0,0],[0,0]],
                                                    "v": [[-30,0],[0,20],[40,-20]],
                                                    "c": False
                                                }
                                            }
                                        },
                                        {
                                            "ty": "st",
                                            "c": {"a": 0, "k": [0, 0.8, 0, 1]},
                                            "o": {"a": 0, "k": 100},
                                            "w": {"a": 0, "k": 12},
                                            "lc": 2
                                        }
                                    ]
                                }
                            ],
                            "ip": 0,
                            "op": 45,
                            "st": 0,
                            "bm": 0
                        }
                    ]
                }
            },
            {
                "id": "business_growth",
                "name": "Business Growth Chart",
                "description": "Animated business growth chart",
                "category": "business",
                "tags": ["business", "growth", "chart", "analytics"],
                "file_url": "embedded://business_growth",
                "thumbnail_url": "https://assets4.lottiefiles.com/packages/lf20_qp1spzqv.json",
                "duration": 3.0,
                "dimensions": {"width": 400, "height": 400},
                "lottie_data": {
                    "v": "5.7.4",
                    "fr": 30,
                    "ip": 0,
                    "op": 90,
                    "w": 400,
                    "h": 400,
                    "nm": "Business Chart",
                    "ddd": 0,
                    "assets": [],
                    "layers": [
                        {
                            "ddd": 0,
                            "ind": 1,
                            "ty": 4,
                            "nm": "Chart",
                            "sr": 1,
                            "ks": {
                                "o": {"a": 0, "k": 100},
                                "r": {"a": 0, "k": 0},
                                "p": {"a": 0, "k": [200, 200, 0]},
                                "a": {"a": 0, "k": [0, 0, 0]},
                                "s": {"a": 0, "k": [100, 100, 100]}
                            },
                            "ao": 0,
                            "shapes": [
                                {
                                    "ty": "gr",
                                    "it": [
                                        {
                                            "ty": "rc",
                                            "p": {"a": 0, "k": [-50, 20]},
                                            "s": {"a": 1, "k": [{"t": 0, "s": [20, 0]}, {"t": 60, "s": [20, 40]}]},
                                            "r": {"a": 0, "k": 4}
                                        },
                                        {
                                            "ty": "fl",
                                            "c": {"a": 0, "k": [0.2, 0.6, 1, 1]},
                                            "o": {"a": 0, "k": 100}
                                        }
                                    ]
                                }
                            ],
                            "ip": 0,
                            "op": 90,
                            "st": 0,
                            "bm": 0
                        }
                    ]
                }
            },
            {
                "id": "heart_like",
                "name": "Heart Like Animation",
                "description": "Social media heart like animation",
                "category": "social",
                "tags": ["social", "like", "heart", "interaction"],
                "file_url": "embedded://heart_like",
                "thumbnail_url": "https://assets1.lottiefiles.com/packages/lf20_d1iq6oo3.json",
                "duration": 1.8,
                "dimensions": {"width": 400, "height": 400},
                "lottie_data": {
                    "v": "5.7.4",
                    "fr": 30,
                    "ip": 0,
                    "op": 54,
                    "w": 400,
                    "h": 400,
                    "nm": "Heart Like",
                    "ddd": 0,
                    "assets": [],
                    "layers": [
                        {
                            "ddd": 0,
                            "ind": 1,
                            "ty": 4,
                            "nm": "Heart",
                            "sr": 1,
                            "ks": {
                                "o": {"a": 0, "k": 100},
                                "r": {"a": 0, "k": 0},
                                "p": {"a": 0, "k": [200, 200, 0]},
                                "a": {"a": 0, "k": [0, 0, 0]},
                                "s": {"a": 1, "k": [{"t": 0, "s": [80, 80, 100]}, {"t": 15, "s": [120, 120, 100]}, {"t": 30, "s": [100, 100, 100]}]}
                            },
                            "ao": 0,
                            "shapes": [
                                {
                                    "ty": "gr",
                                    "it": [
                                        {
                                            "ty": "sh",
                                            "ks": {
                                                "a": 0,
                                                "k": {
                                                    "i": [[0,0],[-10,-10],[0,-15],[10,-10],[20,0],[10,10],[0,15],[-10,10],[-20,0]],
                                                    "o": [[10,10],[10,-10],[0,-15],[-10,-10],[-20,0],[-10,10],[0,15],[10,10],[0,0]],
                                                    "v": [[0,25],[15,10],[25,-10],[15,-25],[-15,-25],[-25,-10],[-25,10],[-15,25],[0,35]],
                                                    "c": True
                                                }
                                            }
                                        },
                                        {
                                            "ty": "fl",
                                            "c": {"a": 0, "k": [1, 0.2, 0.4, 1]},
                                            "o": {"a": 0, "k": 100}
                                        }
                                    ]
                                }
                            ],
                            "ip": 0,
                            "op": 54,
                            "st": 0,
                            "bm": 0
                        }
                    ]
                }
            }
        ]
    
    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session
    
    async def close_session(self):
        """Close HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def search_animations(
        self, 
        query: Optional[str] = None, 
        category: Optional[str] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Search curated animations."""
        try:
            animations = self.curated_animations.copy()
            
            # Filter by query
            if query:
                query_lower = query.lower()
                animations = [
                    anim for anim in animations
                    if query_lower in anim["name"].lower() or
                       query_lower in anim["description"].lower() or
                       any(query_lower in tag.lower() for tag in anim["tags"])
                ]
            
            # Filter by category
            if category:
                animations = [
                    anim for anim in animations
                    if anim["category"].lower() == category.lower()
                ]
            
            # Limit results
            animations = animations[:limit]
            
            return {
                "results": animations,
                "total": len(animations),
                "page": 1,
                "limit": limit,
                "has_more": False
            }
            
        except Exception as e:
            self.logger.error(f"Animation search failed: {e}")
            return {
                "results": [],
                "total": 0,
                "page": 1,
                "limit": limit,
                "has_more": False
            }
    
    async def get_animation_details(self, animation_id: str) -> Optional[AnimationMetadata]:
        """Get detailed information about a specific animation."""
        try:
            for anim_data in self.curated_animations:
                if anim_data["id"] == animation_id:
                    return AnimationMetadata(**anim_data)
            return None
        except Exception as e:
            self.logger.error(f"Failed to get animation details for {animation_id}: {e}")
            return None
    
    async def get_popular_animations(self, category: Optional[str] = None, limit: int = 6) -> List[Dict[str, Any]]:
        """Get popular animations, optionally filtered by category."""
        try:
            animations = self.curated_animations.copy()
            
            if category:
                animations = [
                    anim for anim in animations
                    if anim["category"].lower() == category.lower()
                ]
            
            return animations[:limit]
            
        except Exception as e:
            self.logger.error(f"Failed to get popular animations: {e}")
            return []
    
    async def get_categories(self) -> List[Dict[str, Any]]:
        """Get available animation categories."""
        categories = [
            {"slug": "loading", "name": "Loading & Progress", "description": "Loading indicators and progress animations"},
            {"slug": "success", "name": "Success & Confirmation", "description": "Success confirmations and checkmarks"},
            {"slug": "business", "name": "Business & Finance", "description": "Professional and corporate animations"},
            {"slug": "technology", "name": "Technology", "description": "Tech-related and digital animations"},
            {"slug": "education", "name": "Education", "description": "Educational and learning animations"},
            {"slug": "social", "name": "Social Media", "description": "Social media and networking animations"},
            {"slug": "entertainment", "name": "Entertainment", "description": "Fun and entertaining animations"},
            {"slug": "healthcare", "name": "Healthcare", "description": "Medical and wellness animations"},
        ]
        return categories
    
    async def download_animation(self, file_url: str) -> Optional[Dict[str, Any]]:
        """Download Lottie animation JSON data."""
        try:
            # Handle embedded animations
            if file_url.startswith("embedded://"):
                animation_id = file_url.replace("embedded://", "")
                for anim in self.curated_animations:
                    if anim["id"] == animation_id:
                        return anim.get("lottie_data")
                return None
            
            # For external URLs, attempt to download
            session = await self.get_session()
            async with session.get(file_url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    self.logger.warning(f"Failed to download animation from {file_url}: Status {response.status}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error downloading animation from {file_url}: {e}")
            return None

# Global instance
lottiefiles_service = LottieFilesService()