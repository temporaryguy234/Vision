#!/usr/bin/env python3
"""
Simple test to verify deployment works
Run this after deploying with Emergent
"""
import requests
import json

def test_deployment():
    print("🧪 Testing MotionEdit Deployment...")
    
    # Replace with your actual deployment URL
    base_url = "https://your-emergent-url.com"  # Change this!
    
    tests = [
        ("Health Check", f"{base_url}/health"),
        ("Lottie Import", f"{base_url}/api/test/import-lottie"),
    ]
    
    for test_name, url in tests:
        try:
            if "health" in url:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    print(f"✅ {test_name}: OK")
                else:
                    print(f"❌ {test_name}: Failed ({response.status_code})")
            elif "import-lottie" in url:
                response = requests.post(url, 
                    data={"url": "https://lottie.host/85036dbf-44d5-420d-aa24-325989179/bN9lsInwGh.json"},
                    timeout=30)
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        print(f"✅ {test_name}: OK")
                        print(f"   Thumbnail: {result.get('thumbnail_url', 'N/A')}")
                    else:
                        print(f"❌ {test_name}: Failed - {result.get('error', 'Unknown')}")
                else:
                    print(f"❌ {test_name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {test_name}: Error - {e}")

if __name__ == "__main__":
    print("⚠️  IMPORTANT: Update the base_url variable with your actual Emergent deployment URL!")
    test_deployment()

