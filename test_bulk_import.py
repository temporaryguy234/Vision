#!/usr/bin/env python3
"""
Focused test script for bulk import functionality
"""

import requests
import json
import tempfile
import os
from pathlib import Path

class BulkImportTester:
    def __init__(self, base_url="https://motion-templates-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.test_files_dir = None
        
    def create_test_files(self):
        """Create test files for bulk import testing"""
        self.test_files_dir = Path(tempfile.mkdtemp())
        
        # Create a valid Lottie JSON file
        lottie_data = {
            "v": "5.7.4",
            "fr": 30,
            "ip": 0,
            "op": 60,
            "w": 800,
            "h": 600,
            "nm": "Test Animation",
            "ddd": 0,
            "assets": [],
            "layers": [
                {
                    "ddd": 0,
                    "ind": 1,
                    "ty": 4,
                    "nm": "Shape Layer 1",
                    "sr": 1,
                    "ks": {
                        "o": {"a": 0, "k": 100},
                        "r": {"a": 0, "k": 0},
                        "p": {"a": 0, "k": [400, 300, 0]},
                        "a": {"a": 0, "k": [0, 0, 0]},
                        "s": {"a": 0, "k": [100, 100, 100]}
                    },
                    "ao": 0,
                    "shapes": [],
                    "ip": 0,
                    "op": 60,
                    "st": 0,
                    "bm": 0
                }
            ]
        }
        
        # Save valid Lottie file
        self.lottie_file = self.test_files_dir / "test_animation.json"
        with open(self.lottie_file, 'w') as f:
            json.dump(lottie_data, f)
        
        # Create an invalid JSON file
        self.invalid_json_file = self.test_files_dir / "invalid.json"
        with open(self.invalid_json_file, 'w') as f:
            f.write('{"invalid": "json", "missing": "lottie_fields"}')
        
        # Create a simple PNG file (1x1 pixel)
        self.png_file = self.test_files_dir / "test_image.png"
        # Simple 1x1 PNG file in bytes
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
        with open(self.png_file, 'wb') as f:
            f.write(png_data)
        
        print(f"✅ Created test files in {self.test_files_dir}")

    def cleanup_test_files(self):
        """Clean up test files"""
        import shutil
        if self.test_files_dir and self.test_files_dir.exists():
            shutil.rmtree(self.test_files_dir)
            print("✅ Cleaned up test files")

    def test_bulk_upload(self):
        """Test the bulk upload endpoint"""
        print("\n🔍 Testing Bulk Import Upload...")
        url = f"{self.base_url}/api/bulk-import/upload"
        
        try:
            files = [
                ('files', ('test_animation.json', open(self.lottie_file, 'rb'), 'application/json')),
                ('files', ('test_image.png', open(self.png_file, 'rb'), 'image/png')),
                ('files', ('invalid.json', open(self.invalid_json_file, 'rb'), 'application/json'))
            ]
            
            response = requests.post(url, files=files, timeout=30)
            
            # Close file handles
            for _, (_, file_handle, _) in files:
                file_handle.close()
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                print(f"✅ Upload successful - processed {len(results)} files")
                
                for result in results:
                    filename = result.get('filename')
                    status = result.get('status')
                    asset_type = result.get('asset_type', 'N/A')
                    message = result.get('message', '')
                    
                    print(f"  📁 {filename}: {status} ({asset_type})")
                    if message:
                        print(f"     Message: {message}")
                    
                    if status == 'success':
                        metadata = result.get('metadata', {})
                        print(f"     Metadata: {metadata}")
                        print(f"     File URL: {result.get('file_url')}")
                        print(f"     File Hash: {result.get('file_hash')}")
                
                return True, data
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False, {}
                
        except Exception as e:
            print(f"❌ Error during upload: {str(e)}")
            return False, {}

    def test_create_templates(self, upload_data):
        """Test template creation from upload data"""
        print("\n🔍 Testing Template Creation...")
        
        # Extract successful uploads
        successful_items = []
        for result in upload_data.get('results', []):
            if result.get('status') == 'success':
                successful_items.append({
                    'filename': result.get('filename'),
                    'title': f"Bulk Import - {result.get('filename')}",
                    'category': 'Miscellaneous',
                    'tags': ['bulk-import', 'test'],
                    'file_url': result.get('file_url'),
                    'asset_type': result.get('asset_type'),
                    'metadata': result.get('metadata'),
                    'thumbnail_url': result.get('thumbnail_url'),
                    'file_hash': result.get('file_hash'),
                    'creator_id': 'bulk_import_tester',
                    'is_public': True
                })
        
        if not successful_items:
            print("❌ No successful uploads to create templates from")
            return False, {}
        
        url = f"{self.base_url}/api/bulk-import/create-templates"
        import_data = {'items': successful_items}
        
        try:
            response = requests.post(url, json=import_data, headers={'Content-Type': 'application/json'}, timeout=30)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                templates_created = data.get('templates_created', [])
                errors = data.get('errors', [])
                summary = data.get('summary', {})
                
                print(f"✅ Template creation completed")
                print(f"📊 Summary: {summary}")
                
                for template in templates_created:
                    print(f"  ✅ Created: {template.get('title')} (ID: {template.get('template_id')})")
                
                for error in errors:
                    print(f"  ❌ Error for {error.get('filename')}: {error.get('error')}")
                
                return True, data
            else:
                print(f"❌ Template creation failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False, {}
                
        except Exception as e:
            print(f"❌ Error during template creation: {str(e)}")
            return False, {}

    def test_duplicate_detection(self):
        """Test duplicate file detection"""
        print("\n🔍 Testing Duplicate Detection...")
        url = f"{self.base_url}/api/bulk-import/upload"
        
        try:
            # Upload the same file twice with different names
            files = [
                ('files', ('animation_copy1.json', open(self.lottie_file, 'rb'), 'application/json')),
                ('files', ('animation_copy2.json', open(self.lottie_file, 'rb'), 'application/json'))
            ]
            
            response = requests.post(url, files=files, timeout=30)
            
            # Close file handles
            for _, (_, file_handle, _) in files:
                file_handle.close()
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                print(f"✅ Duplicate test completed - processed {len(results)} files")
                
                success_count = 0
                duplicate_count = 0
                
                for result in results:
                    filename = result.get('filename')
                    status = result.get('status')
                    print(f"  📁 {filename}: {status}")
                    
                    if status == 'success':
                        success_count += 1
                    elif status == 'duplicate':
                        duplicate_count += 1
                        print(f"     Existing template: {result.get('existing_template_id')}")
                
                print(f"📊 Results: {success_count} success, {duplicate_count} duplicates")
                
                if success_count >= 1 and duplicate_count >= 1:
                    print("✅ Duplicate detection working correctly")
                else:
                    print("⚠️  Duplicate detection behavior may need review")
                
                return True, data
            else:
                print(f"❌ Duplicate test failed: {response.status_code}")
                return False, {}
                
        except Exception as e:
            print(f"❌ Error during duplicate test: {str(e)}")
            return False, {}

def main():
    print("🚀 Testing Bulk Import Functionality")
    print("=" * 50)
    
    tester = BulkImportTester()
    
    try:
        # Create test files
        tester.create_test_files()
        
        # Test bulk upload
        upload_success, upload_data = tester.test_bulk_upload()
        
        if upload_success:
            # Test template creation
            tester.test_create_templates(upload_data)
            
            # Test duplicate detection
            tester.test_duplicate_detection()
        else:
            print("❌ Skipping further tests due to upload failure")
    
    finally:
        # Clean up
        tester.cleanup_test_files()
    
    print("\n" + "=" * 50)
    print("🏁 Bulk import testing completed")

if __name__ == "__main__":
    main()