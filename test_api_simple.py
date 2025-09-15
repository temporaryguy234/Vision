#!/usr/bin/env python3
"""
Simple test script to verify the API endpoint
"""
import requests
import json

def test_api():
    """Test the API endpoint"""
    url = "https://lottie.host/85036dbf-44d5-420d-aa24-325988579179/bN9lsInwGh.json"
    
    print(f"Testing API endpoint with URL: {url}")
    
    try:
        # Test the API endpoint
        response = requests.post(
            'http://localhost:8001/api/test/import-lottie',
            data={'url': url},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API endpoint working!")
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ API endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api()
