import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import json
import re

# Try to import OpenAI, fallback if not available
try:
    import openai
    OPENAI_AVAILABLE = True
    openai.api_key = os.environ.get('OPENAI_API_KEY')
except ImportError:
    OPENAI_AVAILABLE = False

class AIPromptRequest(BaseModel):
    prompt: str
    template_id: str
    current_state: Dict[str, Any]
    manifest: Dict[str, Any]

class AIPromptResponse(BaseModel):
    patches: List[Dict[str, Any]]
    explanation: str
    confidence: float

class AIService:
    def __init__(self):
        self.model = "gpt-4"
        self.max_tokens = 1000
    
    async def process_natural_language_prompt(
        self, 
        prompt: str, 
        manifest: Dict[str, Any], 
        current_state: Dict[str, Any]
    ) -> AIPromptResponse:
        """Process natural language prompt and return JSON patches with 100% reliability"""
        
        # Always start with bulletproof fallback processing
        fallback_patches = self._fallback_prompt_processing(prompt, manifest, current_state)
        
        try:
            if not OPENAI_AVAILABLE or not openai.api_key:
                # Use enhanced fallback processing
                return AIPromptResponse(
                    patches=fallback_patches,
                    explanation=f"Enhanced rule-based interpretation: {prompt}",
                    confidence=0.8
                )
            
            # Create system prompt with context
            system_prompt = self._create_system_prompt(manifest, current_state)
            
            # Create user prompt
            user_prompt = f"""
            User wants to: {prompt}
            
            Please analyze this request and return JSON patches to modify the animation.
            Focus on the most likely interpretation of the user's intent.
            
            Return your response as a JSON object with:
            - patches: Array of JSON patch operations
            - explanation: Brief explanation of what changes will be made
            - confidence: Number between 0-1 indicating confidence in interpretation
            
            If you're unsure, return the fallback patches: {json.dumps(fallback_patches)}
            """
            
            # Use new OpenAI API format with timeout and retry
            client = openai.OpenAI(api_key=openai.api_key, timeout=10.0)
            
            for attempt in range(3):  # Try 3 times
                try:
                    response = client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        max_tokens=self.max_tokens,
                        temperature=0.3
                    )
                    
                    content = response.choices[0].message.content
                    
                    # Parse AI response
                    try:
                        ai_response = json.loads(content)
                        # Validate the response
                        if 'patches' in ai_response and isinstance(ai_response['patches'], list):
                            return AIPromptResponse(**ai_response)
                        else:
                            raise ValueError("Invalid AI response format")
                    except (json.JSONDecodeError, ValueError):
                        # Fallback: extract patches from response
                        patches = self._extract_patches_from_text(content, prompt, manifest)
                        if patches:
                            return AIPromptResponse(
                                patches=patches,
                                explanation=f"AI interpreted: {prompt}",
                                confidence=0.7
                            )
                        else:
                            # Use fallback patches if AI extraction fails
                            return AIPromptResponse(
                                patches=fallback_patches,
                                explanation=f"AI failed, using fallback: {prompt}",
                                confidence=0.6
                            )
                    
                except Exception as attempt_error:
                    print(f"AI attempt {attempt + 1} failed: {attempt_error}")
                    if attempt == 2:  # Last attempt
                        break
                    continue
                
        except Exception as e:
            print(f"AI service error: {e}")
        
        # Final fallback - always return something
        return AIPromptResponse(
            patches=fallback_patches,
            explanation=f"Bulletproof fallback: {prompt}",
            confidence=0.8
        )
    
    def _create_system_prompt(self, manifest: Dict[str, Any], current_state: Dict[str, Any]) -> str:
        """Create system prompt with animation context"""
        return f"""
        You are an AI assistant for a motion graphics editor. Users can edit Lottie animations using natural language.
        
        Available editable elements in this animation:
        
        ELEMENTS:
        {json.dumps(manifest.get('elements', []), indent=2)}
        
        CANVAS PROPERTIES:
        {json.dumps(manifest.get('canvas', {}), indent=2)}
        
        Current state:
        {json.dumps(current_state, indent=2)}
        
        You can create JSON patch operations to modify ANY aspect of the animation:
        
        POSITION/LOCATION:
        - Move elements: {{"op": "replace", "path": "/elements/{{element_id}}/x", "value": 50}}
        - Move elements: {{"op": "replace", "path": "/elements/{{element_id}}/y", "value": 30}}
        - Position relative: {{"op": "replace", "path": "/elements/{{element_id}}/position", "value": "center"}}
        
        SIZE/SCALE:
        - Scale elements: {{"op": "replace", "path": "/elements/{{element_id}}/scale", "value": 1.5}}
        - Resize: {{"op": "replace", "path": "/elements/{{element_id}}/width", "value": 200}}
        - Resize: {{"op": "replace", "path": "/elements/{{element_id}}/height", "value": 150}}
        
        FORM/SHAPE:
        - Change shape: {{"op": "replace", "path": "/elements/{{element_id}}/shape", "value": "circle"}}
        - Border radius: {{"op": "replace", "path": "/elements/{{element_id}}/corner_radius", "value": 20}}
        - Stroke width: {{"op": "replace", "path": "/elements/{{element_id}}/stroke_width", "value": 3}}
        
        COLORS:
        - Fill color: {{"op": "replace", "path": "/elements/{{element_id}}/fill_color", "value": "#FF6A00"}}
        - Stroke color: {{"op": "replace", "path": "/elements/{{element_id}}/stroke_color", "value": "#000000"}}
        - Text color: {{"op": "replace", "path": "/elements/{{element_id}}/color", "value": "#FFFFFF"}}
        - Background: {{"op": "replace", "path": "/canvas/background_color", "value": "#F0F0F0"}}
        
        TEXT:
        - Change text: {{"op": "replace", "path": "/elements/{{element_id}}/content", "value": "New Text"}}
        - Font size: {{"op": "replace", "path": "/elements/{{element_id}}/font_size", "value": 24}}
        - Font family: {{"op": "replace", "path": "/elements/{{element_id}}/font_family", "value": "Arial"}}
        - Alignment: {{"op": "replace", "path": "/elements/{{element_id}}/alignment", "value": "center"}}
        
        ANIMATION:
        - Speed: {{"op": "replace", "path": "/canvas/global_playback_speed", "value": 1.5}}
        - Rotation: {{"op": "replace", "path": "/elements/{{element_id}}/rotation", "value": 45}}
        - Opacity: {{"op": "replace", "path": "/elements/{{element_id}}/opacity", "value": 0.8}}
        
        IMAGES:
        - Change image: {{"op": "replace", "path": "/elements/{{element_id}}/source_url", "value": "https://example.com/image.jpg"}}
        - Image fit: {{"op": "replace", "path": "/elements/{{element_id}}/fit", "value": "cover"}}
        
        CANVAS:
        - Canvas size: {{"op": "replace", "path": "/canvas/width", "value": 800}}
        - Canvas size: {{"op": "replace", "path": "/canvas/height", "value": 600}}
        
        Always return valid JSON with patches array, explanation, and confidence score.
        Be creative and interpret user intent broadly - you can modify ANY property of the animation.
        """
    
    def _extract_patches_from_text(self, text: str, prompt: str, manifest: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract patches from AI text response"""
        patches = []
        
        # Look for JSON patches in the response
        json_pattern = r'\{[^}]*"op"[^}]*\}'
        matches = re.findall(json_pattern, text)
        
        for match in matches:
            try:
                patch = json.loads(match)
                if 'op' in patch and 'path' in patch and 'value' in patch:
                    patches.append(patch)
            except:
                continue
        
        # If no patches found, use fallback
        if not patches:
            patches = self._fallback_prompt_processing(prompt, manifest, {})
        
        return patches
    
    def _fallback_prompt_processing(
        self, 
        prompt: str, 
        manifest: Dict[str, Any], 
        current_state: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Enhanced fallback rule-based prompt processing for ALL types of changes"""
        patches = []
        prompt_lower = prompt.lower()
        
        # Get available elements
        elements = manifest.get('elements', [])
        if not elements:
            return patches
        
        # Use first element as default target
        target_element = elements[0]
        element_id = target_element.get('id', 'element_1')
        
        # POSITION/LOCATION changes
        if any(word in prompt_lower for word in ['move', 'position', 'location', 'place', 'center', 'left', 'right', 'top', 'bottom']):
            x_value = 50  # default center
            y_value = 50  # default center
            
            if 'center' in prompt_lower:
                x_value, y_value = 50, 50
            elif 'left' in prompt_lower:
                x_value = 20
            elif 'right' in prompt_lower:
                x_value = 80
            elif 'top' in prompt_lower:
                y_value = 20
            elif 'bottom' in prompt_lower:
                y_value = 80
            
            # Look for specific coordinates
            coord_match = re.search(r'(\d+).*?(\d+)', prompt)
            if coord_match:
                x_value = min(100, max(0, int(coord_match.group(1))))
                y_value = min(100, max(0, int(coord_match.group(2))))
            
            patches.extend([
                {"op": "replace", "path": f"/elements/{element_id}/x", "value": x_value},
                {"op": "replace", "path": f"/elements/{element_id}/y", "value": y_value}
            ])
        
        # SIZE/SCALE changes
        if any(word in prompt_lower for word in ['size', 'scale', 'bigger', 'smaller', 'larger', 'resize']):
            scale_value = 1.0
            
            if 'bigger' in prompt_lower or 'larger' in prompt_lower:
                scale_value = 1.5
            elif 'smaller' in prompt_lower:
                scale_value = 0.7
            
            # Look for specific scale values
            scale_match = re.search(r'(\d+(?:\.\d+)?)', prompt)
            if scale_match:
                scale_value = float(scale_match.group(1))
                if scale_value > 5:
                    scale_value = scale_value / 100  # Convert percentage
            
            patches.append({
                "op": "replace",
                "path": f"/elements/{element_id}/scale",
                "value": min(5.0, max(0.1, scale_value))
            })
        
        # FORM/SHAPE changes
        if any(word in prompt_lower for word in ['shape', 'form', 'circle', 'square', 'rectangle', 'round', 'corner']):
            if 'circle' in prompt_lower or 'round' in prompt_lower:
                patches.append({
                    "op": "replace",
                    "path": f"/elements/{element_id}/shape",
                    "value": "circle"
                })
            elif 'square' in prompt_lower or 'rectangle' in prompt_lower:
                patches.append({
                    "op": "replace",
                    "path": f"/elements/{element_id}/shape",
                    "value": "rectangle"
                })
            
            # Border radius
            radius_match = re.search(r'(\d+)', prompt)
            if radius_match:
                radius_value = int(radius_match.group(1))
                patches.append({
                    "op": "replace",
                    "path": f"/elements/{element_id}/corner_radius",
                    "value": min(100, max(0, radius_value))
                })
        
        # ROTATION changes
        if any(word in prompt_lower for word in ['rotate', 'turn', 'angle', 'degrees']):
            rotation_value = 0
            
            if 'left' in prompt_lower:
                rotation_value = -45
            elif 'right' in prompt_lower:
                rotation_value = 45
            elif 'upside down' in prompt_lower:
                rotation_value = 180
            
            # Look for specific degrees
            degree_match = re.search(r'(\d+)', prompt)
            if degree_match:
                rotation_value = int(degree_match.group(1))
            
            patches.append({
                "op": "replace",
                "path": f"/elements/{element_id}/rotation",
                "value": rotation_value % 360
            })
        
        # OPACITY changes
        if any(word in prompt_lower for word in ['opacity', 'transparent', 'fade', 'visible', 'invisible']):
            opacity_value = 1.0
            
            if 'transparent' in prompt_lower or 'invisible' in prompt_lower:
                opacity_value = 0.0
            elif 'fade' in prompt_lower:
                opacity_value = 0.5
            
            # Look for specific opacity values
            opacity_match = re.search(r'(\d+(?:\.\d+)?)', prompt)
            if opacity_match:
                opacity_value = float(opacity_match.group(1))
                if opacity_value > 1:
                    opacity_value = opacity_value / 100  # Convert percentage
            
            patches.append({
                "op": "replace",
                "path": f"/elements/{element_id}/opacity",
                "value": min(1.0, max(0.0, opacity_value))
            })
        
        # TEXT changes
        text_match = re.search(r'(?:change|set|update).*?(?:text|title|heading).*?(?:to|=)\s*["\']([^"\']+)["\']', prompt, re.I)
        if not text_match:
            text_match = re.search(r'(?:text|title|heading).*?["\']([^"\']+)["\']', prompt, re.I)
        
        if text_match:
            new_text = text_match.group(1)
            patches.append({
                "op": "replace",
                "path": f"/elements/{element_id}/content",
                "value": new_text
            })
        
        # COLOR changes
        color_match = re.search(r'(?:change|set|make).*?color.*?(?:to|=)\s*(#[0-9a-fA-F]{6}|red|blue|green|yellow|orange|purple|pink|black|white)', prompt, re.I)
        if color_match:
            color_value = color_match.group(1)
            
            # Convert named colors to hex
            color_map = {
                'red': '#FF0000', 'blue': '#0000FF', 'green': '#00FF00',
                'yellow': '#FFFF00', 'orange': '#FFA500', 'purple': '#800080',
                'pink': '#FFC0CB', 'black': '#000000', 'white': '#FFFFFF'
            }
            
            if color_value.lower() in color_map:
                color_value = color_map[color_value.lower()]
            
            # Determine color type
            if 'background' in prompt_lower:
                patches.append({
                    "op": "replace",
                    "path": "/canvas/background_color",
                    "value": color_value
                })
            elif 'stroke' in prompt_lower or 'border' in prompt_lower:
                patches.append({
                    "op": "replace",
                    "path": f"/elements/{element_id}/stroke_color",
                    "value": color_value
                })
            else:
                patches.append({
                    "op": "replace",
                    "path": f"/elements/{element_id}/fill_color",
                    "value": color_value
                })
        
        # SPEED changes
        speed_match = re.search(r'(?:speed|faster|slower).*?(\d+(?:\.\d+)?)', prompt, re.I)
        if speed_match:
            speed_value = float(speed_match.group(1))
            
            if 'faster' in prompt_lower:
                speed_value = min(3.0, speed_value)
            elif 'slower' in prompt_lower:
                speed_value = max(0.2, 1.0 / speed_value)
            
            patches.append({
                "op": "replace",
                "path": "/canvas/global_playback_speed",
                "value": speed_value
            })
        elif 'faster' in prompt_lower:
            patches.append({
                "op": "replace",
                "path": "/canvas/global_playback_speed",
                "value": 1.5
            })
        elif 'slower' in prompt_lower:
            patches.append({
                "op": "replace",
                "path": "/canvas/global_playback_speed",
                "value": 0.7
            })
        
        # FONT SIZE changes
        if 'font size' in prompt_lower or 'text size' in prompt_lower:
            size_match = re.search(r'(\d+)', prompt)
            if size_match:
                font_size = int(size_match.group(1))
                patches.append({
                    "op": "replace",
                    "path": f"/elements/{element_id}/font_size",
                    "value": min(180, max(12, font_size))
                })
        
        # CANVAS SIZE changes
        if any(word in prompt_lower for word in ['canvas', 'screen', 'resolution']):
            width_match = re.search(r'(\d+).*?(\d+)', prompt)
            if width_match:
                width = int(width_match.group(1))
                height = int(width_match.group(2))
                patches.extend([
                    {"op": "replace", "path": "/canvas/width", "value": min(2000, max(100, width))},
                    {"op": "replace", "path": "/canvas/height", "value": min(2000, max(100, height))}
                ])
        
        return patches

# Global AI service instance
ai_service = AIService()