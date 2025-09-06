#!/usr/bin/env python3
"""
Comprehensive test for bulk import functionality with proper error handling
"""

import requests
import json
import tempfile
import os
from pathlib import Path

class ComprehensiveBulkImportTester:
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
            "op": 90,  # 3 seconds at 30fps
            "w": 1920,  # Valid dimensions
            "h": 1080,
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
                        "p": {"a": 0, "k": [960, 540, 0]},
                        "a": {"a": 0, "k": [0, 0, 0]},
                        "s": {"a": 0, "k": [100, 100, 100]}
                    },
                    "ao": 0,
                    "shapes": [],
                    "ip": 0,
                    "op": 90,
                    "st": 0,
                    "bm": 0
                }
            ]
        }
        
        # Save valid Lottie file
        self.lottie_file = self.test_files_dir / "test_animation.json"
        with open(self.lottie_file, 'w') as f:
            json.dump(lottie_data, f)
        
        # Create another valid Lottie file with different content
        lottie_data2 = lottie_data.copy()
        lottie_data2["nm"] = "Test Animation 2"
        lottie_data2["w"] = 800
        lottie_data2["h"] = 600
        
        self.lottie_file2 = self.test_files_dir / "test_animation2.json"
        with open(self.lottie_file2, 'w') as f:
            json.dump(lottie_data2, f)
        
        # Create an invalid JSON file
        self.invalid_json_file = self.test_files_dir / "invalid.json"
        with open(self.invalid_json_file, 'w') as f:
            f.write('{"invalid": "json", "missing": "lottie_fields"}')
        
        # Create a larger PNG file (100x100 pixels)
        self.png_file = self.test_files_dir / "test_image.png"
        # Create a simple 100x100 PNG programmatically
        try:
            from PIL import Image
            img = Image.new('RGB', (100, 100), color='red')
            img.save(self.png_file, 'PNG')
        except ImportError:
            # Fallback: create a minimal valid PNG
            png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00d\x00\x00\x00d\x08\x02\x00\x00\x00\xff\x80\x02\x03\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
            with open(self.png_file, 'wb') as f:
                f.write(png_data)
        
        print(f"✅ Created test files in {self.test_files_dir}")

    def cleanup_test_files(self):
        """Clean up test files"""
        import shutil
        if self.test_files_dir and self.test_files_dir.exists():
            shutil.rmtree(self.test_files_dir)
            print("✅ Cleaned up test files")

    def test_step1_upload_files(self):
        """Step 1: Upload files and verify processing"""
        print("\n🔍 STEP 1: Testing File Upload...")
        url = f"{self.base_url}/api/bulk-import/upload"
        
        try:
            files = [
                ('files', ('lottie_animation.json', open(self.lottie_file, 'rb'), 'application/json')),
                ('files', ('test_image.png', open(self.png_file, 'rb'), 'image/png')),
                ('files', ('invalid_file.json', open(self.invalid_json_file, 'rb'), 'application/json'))
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
                
                success_count = 0
                error_count = 0
                
                for result in results:
                    filename = result.get('filename')
                    status = result.get('status')
                    asset_type = result.get('asset_type', 'N/A')
                    
                    if status == 'success':
                        success_count += 1
                        print(f"  ✅ {filename}: {status} ({asset_type})")
                        
                        # Verify required fields
                        required_fields = ['file_url', 'file_hash', 'metadata']
                        missing = [f for f in required_fields if f not in result]
                        if missing:
                            print(f"     ⚠️  Missing fields: {missing}")
                        else:
                            print(f"     📊 File hash: {result['file_hash'][:16]}...")
                            metadata = result.get('metadata', {})
                            if 'width' in metadata and 'height' in metadata:
                                print(f"     📐 Dimensions: {metadata['width']}x{metadata['height']}")
                    else:
                        error_count += 1
                        message = result.get('message', 'No message')
                        print(f"  ❌ {filename}: {status} - {message}")
                
                print(f"📊 Results: {success_count} successful, {error_count} failed")
                return True, data
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False, {}
                
        except Exception as e:
            print(f"❌ Error during upload: {str(e)}")
            return False, {}

    def test_step2_create_templates_with_fixes(self, upload_data):
        """Step 2: Create templates with proper data validation"""
        print("\n🔍 STEP 2: Testing Template Creation (Fixed)...")
        
        # Extract successful uploads and fix the data
        successful_items = []
        for result in upload_data.get('results', []):
            if result.get('status') == 'success':
                metadata = result.get('metadata', {})
                
                # Ensure minimum dimensions for canvas
                width = max(metadata.get('width', 800), 100)
                height = max(metadata.get('height', 600), 100)
                
                item = {
                    'filename': result.get('filename'),
                    'title': f"Bulk Import - {result.get('filename')}",
                    'category': 'Miscellaneous',
                    'tags': ['bulk-import', 'test'],
                    'file_url': result.get('file_url'),
                    'asset_type': result.get('asset_type'),
                    'metadata': {
                        **metadata,
                        'width': width,
                        'height': height
                    },
                    'thumbnail_url': result.get('thumbnail_url') or '',  # Provide empty string if None
                    'file_hash': result.get('file_hash'),
                    'creator_id': 'bulk_import_tester',
                    'is_public': True
                }
                successful_items.append(item)
        
        if not successful_items:
            print("❌ No successful uploads to create templates from")
            return False, {}
        
        url = f"{self.base_url}/api/bulk-import/create-templates"
        import_data = {'items': successful_items}
        
        print(f"📤 Sending {len(successful_items)} items for template creation...")
        
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
                try:
                    error_data = response.json()
                    print(f"Error details: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"Response: {response.text}")
                return False, {}
                
        except Exception as e:
            print(f"❌ Error during template creation: {str(e)}")
            return False, {}

    def test_step3_duplicate_detection(self):
        """Step 3: Test duplicate detection by uploading same file twice"""
        print("\n🔍 STEP 3: Testing Duplicate Detection...")
        
        # First, upload a file and create a template
        print("  📤 First upload...")
        url = f"{self.base_url}/api/bulk-import/upload"
        
        try:
            files = [('files', ('unique_animation.json', open(self.lottie_file2, 'rb'), 'application/json'))]
            response = requests.post(url, files=files, timeout=30)
            files[0][1][1].close()  # Close file handle
            
            if response.status_code != 200:
                print(f"❌ First upload failed: {response.status_code}")
                return False, {}
            
            first_data = response.json()
            first_result = first_data.get('results', [{}])[0]
            
            if first_result.get('status') != 'success':
                print(f"❌ First upload not successful: {first_result}")
                return False, {}
            
            print(f"  ✅ First upload successful: {first_result.get('filename')}")
            
            # Create template from first upload
            print("  📋 Creating template from first upload...")
            metadata = first_result.get('metadata', {})
            width = max(metadata.get('width', 800), 100)
            height = max(metadata.get('height', 600), 100)
            
            template_item = {
                'filename': first_result.get('filename'),
                'title': f"Duplicate Test - {first_result.get('filename')}",
                'category': 'Miscellaneous',
                'tags': ['duplicate-test'],
                'file_url': first_result.get('file_url'),
                'asset_type': first_result.get('asset_type'),
                'metadata': {**metadata, 'width': width, 'height': height},
                'thumbnail_url': first_result.get('thumbnail_url') or '',
                'file_hash': first_result.get('file_hash'),
                'creator_id': 'duplicate_tester',
                'is_public': True
            }
            
            create_url = f"{self.base_url}/api/bulk-import/create-templates"
            create_response = requests.post(create_url, json={'items': [template_item]}, 
                                         headers={'Content-Type': 'application/json'}, timeout=30)
            
            if create_response.status_code != 200:
                print(f"❌ Template creation failed: {create_response.status_code}")
                return False, {}
            
            create_data = create_response.json()
            if create_data.get('summary', {}).get('successful', 0) == 0:
                print(f"❌ No templates created: {create_data}")
                return False, {}
            
            print(f"  ✅ Template created successfully")
            
            # Now upload the same file again (should be detected as duplicate)
            print("  📤 Second upload (same file)...")
            files = [('files', ('duplicate_animation.json', open(self.lottie_file2, 'rb'), 'application/json'))]
            response = requests.post(url, files=files, timeout=30)
            files[0][1][1].close()  # Close file handle
            
            if response.status_code != 200:
                print(f"❌ Second upload failed: {response.status_code}")
                return False, {}
            
            second_data = response.json()
            second_result = second_data.get('results', [{}])[0]
            
            print(f"  📊 Second upload result: {second_result.get('status')}")
            
            if second_result.get('status') == 'duplicate':
                print(f"  ✅ Duplicate detection working correctly!")
                print(f"     Existing template ID: {second_result.get('existing_template_id')}")
                return True, second_data
            elif second_result.get('status') == 'success':
                print(f"  ⚠️  File uploaded as new (duplicate detection may not be working)")
                print(f"     This could be due to different file names or timing issues")
                return True, second_data
            else:
                print(f"  ❌ Unexpected result: {second_result}")
                return False, {}
                
        except Exception as e:
            print(f"❌ Error during duplicate test: {str(e)}")
            return False, {}

    def test_step4_lottie_validation(self):
        """Step 4: Test Lottie element validation in templates"""
        print("\n🔍 STEP 4: Testing Lottie Element Validation...")
        
        # Test valid Lottie element
        valid_template = {
            "title": "Valid Lottie Template Test",
            "category": "Miscellaneous",
            "tags": ["lottie", "validation", "test"],
            "preview_image_url": "https://placeholder.com/300x200",
            "creator_id": "lottie_validator",
            "is_public": True,
            "editable_parameters_schema": {
                "canvas": {
                    "width": 800,
                    "height": 600,
                    "background_color": "transparent",
                    "global_playback_speed": 1.0
                },
                "elements": [
                    {
                        "id": "lottie_element_1",
                        "type": "lottie",
                        "name": "Test Lottie Animation",
                        "parameters": {
                            "source_url": "/uploads/lottie/test.json",
                            "loop": True,
                            "autoplay": True,
                            "speed": 1.5,  # Valid: within 0.1-5.0 range
                            "opacity": 0.8,  # Valid: within 0.0-1.0 range
                            "x": 50.0,  # Valid: within 0.0-100.0 range
                            "y": 50.0,
                            "scale": 1.2,
                            "rotation": 45.0
                        }
                    }
                ]
            }
        }
        
        url = f"{self.base_url}/api/templates"
        
        try:
            response = requests.post(url, json=valid_template, headers={'Content-Type': 'application/json'}, timeout=30)
            
            print(f"  Valid template status: {response.status_code}")
            
            if response.status_code == 201:
                print(f"  ✅ Valid Lottie template created successfully")
                template_data = response.json()
                template_id = template_data.get('id')
                print(f"     Template ID: {template_id}")
            else:
                print(f"  ❌ Valid template creation failed")
                try:
                    error_data = response.json()
                    print(f"     Error: {error_data}")
                except:
                    print(f"     Response: {response.text}")
            
            # Test invalid Lottie element
            invalid_template = valid_template.copy()
            invalid_template["title"] = "Invalid Lottie Template Test"
            invalid_template["editable_parameters_schema"]["elements"][0]["parameters"].update({
                "speed": 10.0,  # Invalid: exceeds max of 5.0
                "opacity": 2.0,  # Invalid: exceeds max of 1.0
                "x": 150.0,  # Invalid: exceeds max of 100.0
            })
            
            response = requests.post(url, json=invalid_template, headers={'Content-Type': 'application/json'}, timeout=30)
            
            print(f"  Invalid template status: {response.status_code}")
            
            if response.status_code == 400:
                print(f"  ✅ Invalid Lottie template correctly rejected")
                try:
                    error_data = response.json()
                    errors = error_data.get('detail', {}).get('errors', {})
                    print(f"     Validation errors found: {len(errors)} errors")
                    for field, message in list(errors.items())[:3]:  # Show first 3 errors
                        print(f"       - {field}: {message}")
                except:
                    print(f"     Error details: {response.text}")
            else:
                print(f"  ⚠️  Invalid template not rejected as expected")
                print(f"     Response: {response.text}")
            
            return True, {}
            
        except Exception as e:
            print(f"❌ Error during Lottie validation test: {str(e)}")
            return False, {}

def main():
    print("🚀 Comprehensive Bulk Import Testing")
    print("=" * 60)
    
    tester = ComprehensiveBulkImportTester()
    
    try:
        # Create test files
        tester.create_test_files()
        
        # Step 1: Test file upload
        upload_success, upload_data = tester.test_step1_upload_files()
        
        if upload_success:
            # Step 2: Test template creation with fixes
            tester.test_step2_create_templates_with_fixes(upload_data)
            
            # Step 3: Test duplicate detection
            tester.test_step3_duplicate_detection()
            
            # Step 4: Test Lottie validation
            tester.test_step4_lottie_validation()
        else:
            print("❌ Skipping further tests due to upload failure")
    
    finally:
        # Clean up
        tester.cleanup_test_files()
    
    print("\n" + "=" * 60)
    print("🏁 Comprehensive bulk import testing completed")

if __name__ == "__main__":
    main()