#!/usr/bin/env python3
"""
Test script to verify Lottie import functionality
"""
import asyncio
import aiohttp
import json

async def test_lottie_import():
    """Test importing the specific Lottie file"""
    url = "https://lottie.host/85036dbf-44d5-420d-aa24-325988579179/bN9lsInwGh.json"
    
    print(f"Testing import of: {url}")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test the Lottie processor directly
            from backend.lottie_processor import lottie_processor
            
            print("Processing Lottie file...")
            animation_data, manifest = await lottie_processor.process_url(url)
            
            print("✅ Successfully processed Lottie file!")
            print(f"Version: {animation_data.get('v')}")
            print(f"Dimensions: {animation_data.get('w')}x{animation_data.get('h')}")
            print(f"Frame Rate: {animation_data.get('fr')} fps")
            print(f"Duration: {animation_data.get('op', 0) - animation_data.get('ip', 0)} frames")
            print(f"Layers: {len(animation_data.get('layers', []))}")
            print(f"Manifest elements: {len(manifest.get('text', []))} text, {len(manifest.get('colors', []))} colors")
            
            # Test the API endpoint
            print("\nTesting API endpoint...")
            form_data = aiohttp.FormData()
            form_data.add_field('url', url)
            
            async with session.post('http://localhost:8001/api/test/import-lottie', data=form_data) as response:
                if response.status == 200:
                    result = await response.json()
                    print("✅ API endpoint working!")
                    print(f"Response: {json.dumps(result, indent=2)}")
                else:
                    print(f"❌ API endpoint failed: {response.status}")
                    print(await response.text())
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_lottie_import())
