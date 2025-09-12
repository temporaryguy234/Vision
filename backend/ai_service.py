import os
import openai
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import json
import re

# OpenAI Configuration
openai.api_key = os.environ.get('OPENAI_API_KEY')

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
        """Process natural language prompt and return JSON patches"""
        
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
        """
        
        try:
            response = await openai.ChatCompletion.acreate(
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
                return AIPromptResponse(**ai_response)
            except json.JSONDecodeError:
                # Fallback: extract patches from response
                patches = self._extract_patches_from_text(content, prompt, manifest)
                return AIPromptResponse(
                    patches=patches,
                    explanation=f"Interpreted: {prompt}",
                    confidence=0.7
                )
                
        except Exception as e:
            print(f"AI service error: {e}")
            # Fallback to rule-based processing
            patches = self._fallback_prompt_processing(prompt, manifest, current_state)
            return AIPromptResponse(
                patches=patches,
                explanation=f"Rule-based interpretation: {prompt}",
                confidence=0.5
            )
    
    def _create_system_prompt(self, manifest: Dict[str, Any], current_state: Dict[str, Any]) -> str:
        """Create system prompt with animation context"""
        return f"""
        You are an AI assistant for a motion graphics editor. Users can edit Lottie animations using natural language.
        
        Available editable elements in this animation:
        
        TEXT ELEMENTS:
        {json.dumps(manifest.get('text', []), indent=2)}
        
        COLOR ELEMENTS:
        {json.dumps(manifest.get('colors', []), indent=2)}
        
        IMAGE ELEMENTS:
        {json.dumps(manifest.get('images', []), indent=2)}
        
        CHART ELEMENTS:
        {json.dumps(manifest.get('chart', []), indent=2)}
        
        SPEED CONTROL:
        {json.dumps(manifest.get('speed', {}), indent=2)}
        
        Current state:
        {json.dumps(current_state, indent=2)}
        
        You can create JSON patch operations with these formats:
        
        1. Text changes: {{"op": "replace", "path": "/text/{{element_id}}", "value": "new text"}}
        2. Color changes: {{"op": "replace", "path": "/colors/{{element_id}}", "value": "#FF6A00"}}
        3. Image changes: {{"op": "replace", "path": "/images/{{element_id}}", "value": "https://example.com/image.jpg"}}
        4. Speed changes: {{"op": "replace", "path": "/speed", "value": 1.5}}
        5. Chart data: {{"op": "replace", "path": "/chart/data", "value": [10, 20, 30, 40]}}
        
        Always return valid JSON with patches array, explanation, and confidence score.
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
        """Fallback rule-based prompt processing"""
        patches = []
        prompt_lower = prompt.lower()
        
        # Text changes
        text_match = re.search(r'(?:change|set|update).*?(?:text|title|heading).*?(?:to|=)\s*["\']([^"\']+)["\']', prompt, re.I)
        if not text_match:
            text_match = re.search(r'(?:text|title|heading).*?["\']([^"\']+)["\']', prompt, re.I)
        
        if text_match and manifest.get('text'):
            new_text = text_match.group(1)
            # Use first text element
            first_text = manifest['text'][0]
            patches.append({
                "op": "replace",
                "path": f"/text/{first_text['id']}",
                "value": new_text
            })
        
        # Color changes
        color_match = re.search(r'(?:change|set|make).*?color.*?(?:to|=)\s*(#[0-9a-fA-F]{6}|red|blue|green|yellow|orange|purple|pink|black|white)', prompt, re.I)
        if color_match and manifest.get('colors'):
            color_value = color_match.group(1)
            
            # Convert named colors to hex
            color_map = {
                'red': '#FF0000', 'blue': '#0000FF', 'green': '#00FF00',
                'yellow': '#FFFF00', 'orange': '#FFA500', 'purple': '#800080',
                'pink': '#FFC0CB', 'black': '#000000', 'white': '#FFFFFF'
            }
            
            if color_value.lower() in color_map:
                color_value = color_map[color_value.lower()]
            
            # Use first color element
            first_color = manifest['colors'][0]
            patches.append({
                "op": "replace",
                "path": f"/colors/{first_color['id']}",
                "value": color_value
            })
        
        # Speed changes
        speed_match = re.search(r'(?:speed|faster|slower).*?(\d+(?:\.\d+)?)', prompt, re.I)
        if speed_match:
            speed_value = float(speed_match.group(1))
            
            if 'faster' in prompt_lower:
                speed_value = min(3.0, speed_value)
            elif 'slower' in prompt_lower:
                speed_value = max(0.2, 1.0 / speed_value)
            
            patches.append({
                "op": "replace",
                "path": "/speed",
                "value": speed_value
            })
        elif 'faster' in prompt_lower:
            patches.append({
                "op": "replace",
                "path": "/speed",
                "value": 1.5
            })
        elif 'slower' in prompt_lower:
            patches.append({
                "op": "replace",
                "path": "/speed",
                "value": 0.7
            })
        
        # Image changes
        image_match = re.search(r'(?:change|replace|set).*?(?:image|logo|picture).*?(?:to|=)\s*(https?://\S+)', prompt, re.I)
        if image_match and manifest.get('images'):
            image_url = image_match.group(1)
            first_image = manifest['images'][0]
            patches.append({
                "op": "replace",
                "path": f"/images/{first_image['id']}",
                "value": image_url
            })
        
        return patches

# Global AI service instance
ai_service = AIService()