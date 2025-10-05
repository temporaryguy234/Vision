"""
AI Service - Simple fallback implementation
"""
from pydantic import BaseModel
from typing import Dict, Any, List

class AIPromptRequest(BaseModel):
    prompt: str
    state: Dict[str, Any]
    manifest: Dict[str, Any]

class AIPromptResponse(BaseModel):
    patches: List[Dict[str, Any]]
    explanation: str
    confidence: float

class AIService:
    """Simple AI service with fallback functionality"""
    
    def __init__(self):
        pass
    
    async def process_natural_language_prompt(
        self, 
        prompt: str, 
        manifest: Dict[str, Any], 
        current_state: Dict[str, Any]
    ) -> AIPromptResponse:
        """Process natural language prompt with fallback"""
        try:
            # Simple rule-based processing
            patches = []
            explanation = "Processed with fallback AI"
            confidence = 0.5
            
            prompt_lower = prompt.lower()
            
            # Handle common commands
            if "faster" in prompt_lower or "speed" in prompt_lower:
                patches.append({
                    "op": "replace",
                    "path": "/canvas/global_playback_speed",
                    "value": 1.5
                })
                explanation = "Increased animation speed"
            
            if "slower" in prompt_lower:
                patches.append({
                    "op": "replace", 
                    "path": "/canvas/global_playback_speed",
                    "value": 0.5
                })
                explanation = "Decreased animation speed"
            
            if "color" in prompt_lower or "colour" in prompt_lower:
                # Extract color if present
                import re
                color_match = re.search(r'#([0-9a-fA-F]{6})', prompt)
                if color_match:
                    color = '#' + color_match.group(1)
                    patches.append({
                        "op": "replace",
                        "path": "/elements/0/fill_color",
                        "value": color
                    })
                    explanation = f"Changed color to {color}"
            
            return AIPromptResponse(
                patches=patches,
                explanation=explanation,
                confidence=confidence
            )
            
        except Exception as e:
            print(f"AI processing error: {e}")
            return AIPromptResponse(
                patches=[],
                explanation="AI processing failed",
                confidence=0.0
            )

# Global instance
ai_service = AIService()