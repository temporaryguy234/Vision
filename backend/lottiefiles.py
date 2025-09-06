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
        
        # Curated list of high-quality Lottie animations
        self.curated_animations = [
            {
                "id": "loading_spinner",
                "name": "Loading Spinner",
                "description": "Elegant loading animation",
                "category": "loading",
                "tags": ["loading", "spinner", "progress"],
                "file_url": "https://lottie.host/4f8c5972-0e6c-4666-8d3d-7a7ad6b49138/FApNKFZP0D.json",
                "thumbnail_url": "https://cdn.lottiefiles.com/images/1795-loading-icon.gif",
                "duration": 2.0,
                "dimensions": {"width": 400, "height": 400}
            },
            {
                "id": "success_checkmark",
                "name": "Success Checkmark",
                "description": "Animated success confirmation",
                "category": "success",
                "tags": ["success", "check", "done", "complete"],
                "file_url": "https://lottie.host/a5e0f66f-dc30-4cc7-bee4-d14e7f8ae5e2/JnMcAiIUaN.json",
                "thumbnail_url": "https://cdn.lottiefiles.com/images/2634-success-check.gif",
                "duration": 1.5,
                "dimensions": {"width": 400, "height": 400}
            },
            {
                "id": "business_growth",
                "name": "Business Growth",
                "description": "Chart showing business growth",
                "category": "business",
                "tags": ["business", "growth", "chart", "analytics"],
                "file_url": "https://lottie.host/5b7c1d3a-c8b2-4ed7-a9b5-fb3f2a1e0c2d/BusinessGrowth.json",
                "thumbnail_url": "https://cdn.lottiefiles.com/images/business-growth.gif",
                "duration": 3.0,
                "dimensions": {"width": 400, "height": 400}
            },
            {
                "id": "social_media",
                "name": "Social Media Icons",
                "description": "Animated social media icons",
                "category": "social",
                "tags": ["social", "media", "icons", "network"],
                "file_url": "https://lottie.host/9c8d7e6f-a1b2-4f5e-8d9c-1a2b3c4d5e6f/SocialMedia.json",
                "thumbnail_url": "https://cdn.lottiefiles.com/images/social-media.gif",
                "duration": 2.5,
                "dimensions": {"width": 400, "height": 400}
            },
            {
                "id": "tech_innovation",
                "name": "Tech Innovation",
                "description": "Technology and innovation animation",
                "category": "technology",
                "tags": ["technology", "innovation", "digital", "future"],
                "file_url": "https://lottie.host/1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d/TechInnovation.json",
                "thumbnail_url": "https://cdn.lottiefiles.com/images/tech-innovation.gif",
                "duration": 4.0,
                "dimensions": {"width": 400, "height": 400}
            },
            {
                "id": "education_learning",
                "name": "Education & Learning",
                "description": "Educational animation with books and graduation",
                "category": "education",
                "tags": ["education", "learning", "books", "school"],
                "file_url": "https://lottie.host/6f7a8b9c-0d1e-2f3a-4b5c-6d7e8f9a0b1c/Education.json",
                "thumbnail_url": "https://cdn.lottiefiles.com/images/education.gif",
                "duration": 3.5,
                "dimensions": {"width": 400, "height": 400}
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