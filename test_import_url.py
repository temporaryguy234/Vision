#!/usr/bin/env python3
"""
Test the main import URL endpoint
"""
import requests
import json

def test_import_url():
    """Test the import URL endpoint"""
    url = "https://lottie.host/85036dbf-44d5-420d-aa24-325988579179/bN9lsInwGh.json"
    
    print(f"Testing import URL endpoint with: {url}")
    
    try:
        # Test the main import URL endpoint
        response = requests.post(
            'http://localhost:8001/api/templates/import-url',
            data={'url': url},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Import URL endpoint working!")
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Import URL endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_import_url()
