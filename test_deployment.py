#!/usr/bin/env python3
"""
Test script to verify deployment functionality
"""
import requests
import json
import time

def test_backend_health():
    """Test if backend is responding"""
    try:
        response = requests.get('http://localhost:8001/health', timeout=5)
        if response.status_code == 200:
            print("✅ Backend health check: OK")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not responding: {e}")
        return False

def test_lottie_import():
    """Test Lottie import functionality"""
    try:
        test_url = "https://lottie.host/85036dbf-44d5-420d-aa24-325989179/bN9lsInwGh.json"
        response = requests.post(
            'http://localhost:8001/api/test/import-lottie',
            data={'url': test_url},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Lottie import test: OK")
                print(f"   - Animation data: {result.get('animation_data', {})}")
                print(f"   - Thumbnail: {result.get('thumbnail_url', 'N/A')}")
                return True
            else:
                print(f"❌ Lottie import failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Lottie import HTTP error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Lottie import test failed: {e}")
        return False

def test_thumbnail_generation():
    """Test thumbnail generation"""
    try:
        # First import a Lottie file
        test_url = "https://lottie.host/85036dbf-44d5-420d-aa24-325989179/bN9lsInwGh.json"
        response = requests.post(
            'http://localhost:8001/api/test/import-lottie',
            data={'url': test_url},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            thumbnail_url = result.get('thumbnail_url')
            if thumbnail_url:
                # Test if thumbnail is accessible
                thumb_response = requests.get(f'http://localhost:8001{thumbnail_url}', timeout=10)
                if thumb_response.status_code == 200:
                    print("✅ Thumbnail generation: OK")
                    return True
                else:
                    print(f"❌ Thumbnail not accessible: {thumb_response.status_code}")
                    return False
            else:
                print("❌ No thumbnail URL returned")
                return False
        else:
            print(f"❌ Cannot test thumbnail - import failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Thumbnail test failed: {e}")
        return False

def main():
    print("🧪 Testing MotionEdit Deployment...")
    print("=" * 50)
    
    # Wait a bit for services to start
    print("⏳ Waiting for services to start...")
    time.sleep(5)
    
    tests = [
        ("Backend Health", test_backend_health),
        ("Lottie Import", test_lottie_import),
        ("Thumbnail Generation", test_thumbnail_generation),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Deployment is working correctly.")
    else:
        print("⚠️  SOME TESTS FAILED! Check the logs above for details.")
        print("\n🔧 TROUBLESHOOTING TIPS:")
        print("1. Check if backend is running: docker ps")
        print("2. Check backend logs: docker logs motionedit-backend")
        print("3. Check if all dependencies are installed")
        print("4. Verify environment variables are set correctly")

if __name__ == "__main__":
    main()

