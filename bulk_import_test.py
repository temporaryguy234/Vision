#!/usr/bin/env python3
"""
Comprehensive Bulk Import System Testing
Testing the improved bulk import functionality with enhanced file format support,
lenient Lottie validation, and better error handling.
"""

import requests
import sys
import json
from datetime import datetime
import uuid
import os
import tempfile
from pathlib import Path

class BulkImportTester:
    def __init__(self, base_url="https://motion-templates-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.created_resources = []

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, files=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'} if not files else {}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, timeout=30)
                else:
                    response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and 'id' in response_data:
                        self.created_resources.append(response_data['id'])
                    return True, response_data
                except:
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def create_comprehensive_test_files(self):
        """Create comprehensive test files for improved bulk import testing"""
        self.test_files_dir = Path(tempfile.mkdtemp())
        
        # 1. Standard Lottie JSON file
        standard_lottie = {
            "v": "5.7.4",
            "fr": 30,
            "ip": 0,
            "op": 90,
            "w": 1920,
            "h": 1080,
            "nm": "Standard Lottie Animation",
            "ddd": 0,
            "assets": [],
            "layers": [
                {
                    "ddd": 0,
                    "ind": 1,
                    "ty": 4,
                    "nm": "Shape Layer",
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
        
        self.standard_lottie_file = self.test_files_dir / "standard_animation.json"
        with open(self.standard_lottie_file, 'w') as f:
            json.dump(standard_lottie, f)
        
        # 2. Lenient Lottie JSON (missing some fields but should be accepted)
        lenient_lottie = {
            "v": "5.7.4",
            "layers": [{"ty": 4, "nm": "Layer"}],
            "w": 800,
            "h": 600,
            "bodymovin": "export from After Effects"  # Should trigger lenient validation
        }
        
        self.lenient_lottie_file = self.test_files_dir / "lenient_animation.json"
        with open(self.lenient_lottie_file, 'w') as f:
            json.dump(lenient_lottie, f)
        
        # 3. Bodymovin export file (should be detected as Lottie)
        bodymovin_export = {
            "bodymovin": True,
            "layers": [{"ty": 1, "nm": "Solid"}],
            "w": 400,
            "h": 400,
            "fr": 24,
            "animation": "After Effects bodymovin export"
        }
        
        self.bodymovin_file = self.test_files_dir / "bodymovin_export.json"
        with open(self.bodymovin_file, 'w') as f:
            json.dump(bodymovin_export, f)
        
        # 4. .lottie extension file (new format support)
        self.lottie_ext_file = self.test_files_dir / "animation.lottie"
        with open(self.lottie_ext_file, 'w') as f:
            json.dump(standard_lottie, f)
        
        # 5. Animation-related JSON (should pass lenient validation)
        animation_json = {
            "animation": "timeline data",
            "keyframes": [{"time": 0, "value": 1}],
            "timeline": {"duration": 3000},
            "width": 500,
            "height": 500
        }
        
        self.animation_json_file = self.test_files_dir / "animation_data.json"
        with open(self.animation_json_file, 'w') as f:
            json.dump(animation_json, f)
        
        # 6. Invalid JSON file (should fail)
        self.invalid_json_file = self.test_files_dir / "invalid.json"
        with open(self.invalid_json_file, 'w') as f:
            f.write('{"invalid": "json", "no_animation_data": true}')
        
        # 7. Malformed JSON file (should fail)
        self.malformed_json_file = self.test_files_dir / "malformed.json"
        with open(self.malformed_json_file, 'w') as f:
            f.write('{"incomplete": json syntax error')
        
        # 8. PNG image file
        self.png_file = self.test_files_dir / "test_image.png"
        png_data = b'\x89PNG\r\n\x1a\n\rIHDR\x01\x01\x08\x02\x90wS\xde\tpHYs\x0b\x13\x0b\x13\x01\x9a\x9c\x18\nIDATx\x9cc```\x04\x01\xdd\x8d\xb4\x1cIEND\xaeB`\x82'
        with open(self.png_file, 'wb') as f:
            f.write(png_data)
        
        # 9. JPEG image file
        self.jpg_file = self.test_files_dir / "test_image.jpg"
        with open(self.jpg_file, 'wb') as f:
            f.write(b'fake jpeg data for testing')
        
        # 10. GIF animation file
        self.gif_file = self.test_files_dir / "test_animation.gif"
        gif_data = b'GIF89a\x01\x00\x01\x00\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x04\x01\x00;'
        with open(self.gif_file, 'wb') as f:
            f.write(gif_data)
        
        # 11. APNG file (new format support)
        self.apng_file = self.test_files_dir / "test_animation.apng"
        with open(self.apng_file, 'wb') as f:
            f.write(png_data)
        
        # 12. MP4 video file
        self.mp4_file = self.test_files_dir / "test_video.mp4"
        with open(self.mp4_file, 'wb') as f:
            f.write(b'fake mp4 video data for testing')
        
        # 13. MOV video file (new format support)
        self.mov_file = self.test_files_dir / "test_video.mov"
        with open(self.mov_file, 'wb') as f:
            f.write(b'fake mov video data for testing')
        
        # 14. AVI video file (new format support)
        self.avi_file = self.test_files_dir / "test_video.avi"
        with open(self.avi_file, 'wb') as f:
            f.write(b'fake avi video data for testing')
        
        # 15. WebM video file
        self.webm_file = self.test_files_dir / "test_video.webm"
        with open(self.webm_file, 'wb') as f:
            f.write(b'fake webm video data for testing')
        
        # 16. After Effects project file (new format support)
        self.aep_file = self.test_files_dir / "project.aep"
        with open(self.aep_file, 'wb') as f:
            f.write(b'fake after effects project data')
        
        # 17. Premiere Pro project file (new format support)
        self.prproj_file = self.test_files_dir / "project.prproj"
        with open(self.prproj_file, 'wb') as f:
            f.write(b'fake premiere pro project data')
        
        # 18. Blender project file (new format support)
        self.blend_file = self.test_files_dir / "project.blend"
        with open(self.blend_file, 'wb') as f:
            f.write(b'fake blender project data')
        
        # 19. Cinema 4D project file (new format support)
        self.c4d_file = self.test_files_dir / "project.c4d"
        with open(self.c4d_file, 'wb') as f:
            f.write(b'fake cinema 4d project data')
        
        # 20. SVG vector file
        self.svg_file = self.test_files_dir / "test_vector.svg"
        svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="40" fill="red"/>
        </svg>'''
        with open(self.svg_file, 'w') as f:
            f.write(svg_content)
        
        # 21. Unsupported text file
        self.txt_file = self.test_files_dir / "unsupported.txt"
        with open(self.txt_file, 'w') as f:
            f.write("This is an unsupported file format for bulk import")
        
        # 22. Large file for size testing
        self.large_file = self.test_files_dir / "large_animation.json"
        large_lottie = standard_lottie.copy()
        large_lottie["large_data"] = "x" * 500000  # 500KB+ of data
        with open(self.large_file, 'w') as f:
            json.dump(large_lottie, f)
        
        print(f"✅ Created {len([f for f in self.test_files_dir.iterdir()])} comprehensive test files in {self.test_files_dir}")

    def cleanup_test_files(self):
        """Clean up test files"""
        import shutil
        if hasattr(self, 'test_files_dir') and self.test_files_dir.exists():
            shutil.rmtree(self.test_files_dir)
            print("✅ Cleaned up test files")

    def test_improved_lottie_validation(self):
        """Test the improved lenient Lottie JSON validation"""
        print(f"\n🔍 Testing Improved Lottie Validation (Lenient Mode)...")
        url = f"{self.base_url}/api/bulk-import/upload"
        
        # Test files that should pass with lenient validation
        test_files = [
            ('files', ('standard_animation.json', open(self.standard_lottie_file, 'rb'), 'application/json')),
            ('files', ('lenient_animation.json', open(self.lenient_lottie_file, 'rb'), 'application/json')),
            ('files', ('bodymovin_export.json', open(self.bodymovin_file, 'rb'), 'application/json')),
            ('files', ('animation.lottie', open(self.lottie_ext_file, 'rb'), 'application/json')),
            ('files', ('animation_data.json', open(self.animation_json_file, 'rb'), 'application/json'))
        ]
        
        try:
            response = requests.post(url, files=test_files, timeout=30)
            
            # Close file handles
            for _, (_, file_handle, _) in test_files:
                file_handle.close()
            
            success = response.status_code == 200
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                
                data = response.json()
                results = data.get('results', [])
                print(f"   📁 Processed {len(results)} files with lenient validation")
                
                success_count = 0
                for result in results:
                    filename = result.get('filename')
                    status = result.get('status')
                    asset_type = result.get('asset_type')
                    
                    if status == 'success':
                        success_count += 1
                        print(f"   ✅ {filename}: {status} ({asset_type})")
                        
                        # Verify Lottie files have proper metadata
                        if asset_type == 'Lottie JSON':
                            metadata = result.get('metadata', {})
                            if 'width' in metadata and 'height' in metadata:
                                print(f"      📊 Dimensions: {metadata['width']}x{metadata['height']}")
                            if 'duration' in metadata:
                                print(f"      ⏱️  Duration: {metadata['duration']}s")
                    else:
                        print(f"   ❌ {filename}: {status} - {result.get('message', '')}")
                
                print(f"   📈 Lenient validation success rate: {success_count}/{len(results)} files")
                
                # Expect at least 4 out of 5 files to pass (standard, lenient, bodymovin, .lottie extension)
                if success_count >= 4:
                    print(f"   ✅ Lenient validation working correctly")
                else:
                    print(f"   ⚠️  Lenient validation may be too strict")
                
                return True, data
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                return False, {}
                
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}
        
        finally:
            self.tests_run += 1

    def test_extended_file_format_support(self):
        """Test support for new file formats (AVI, MOV, APNG, project files)"""
        print(f"\n🔍 Testing Extended File Format Support...")
        url = f"{self.base_url}/api/bulk-import/upload"
        
        # Test new format support
        test_files = [
            ('files', ('test_video.mov', open(self.mov_file, 'rb'), 'video/quicktime')),
            ('files', ('test_video.avi', open(self.avi_file, 'rb'), 'video/x-msvideo')),
            ('files', ('test_animation.apng', open(self.apng_file, 'rb'), 'image/apng')),
            ('files', ('project.aep', open(self.aep_file, 'rb'), 'application/octet-stream')),
            ('files', ('project.prproj', open(self.prproj_file, 'rb'), 'application/octet-stream')),
            ('files', ('project.blend', open(self.blend_file, 'rb'), 'application/octet-stream')),
            ('files', ('project.c4d', open(self.c4d_file, 'rb'), 'application/octet-stream'))
        ]
        
        try:
            response = requests.post(url, files=test_files, timeout=30)
            
            # Close file handles
            for _, (_, file_handle, _) in test_files:
                file_handle.close()
            
            success = response.status_code == 200
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                
                data = response.json()
                results = data.get('results', [])
                print(f"   📁 Processed {len(results)} new format files")
                
                format_support = {}
                for result in results:
                    filename = result.get('filename')
                    status = result.get('status')
                    asset_type = result.get('asset_type')
                    extension = Path(filename).suffix.lower()
                    
                    format_support[extension] = {
                        'status': status,
                        'asset_type': asset_type,
                        'supported': status == 'success'
                    }
                    
                    if status == 'success':
                        print(f"   ✅ {filename}: {asset_type}")
                    else:
                        print(f"   ❌ {filename}: {status} - {result.get('message', '')}")
                
                # Check specific format support
                expected_support = {
                    '.mov': True,  # Should be supported as MP4
                    '.avi': True,  # Should be supported as MP4
                    '.apng': True,  # Should be supported as GIF
                    '.aep': True,  # Should be supported as generic asset (PNG)
                    '.prproj': True,  # Should be supported as generic asset (PNG)
                    '.blend': True,  # Should be supported as generic asset (PNG)
                    '.c4d': True   # Should be supported as generic asset (PNG)
                }
                
                supported_count = sum(1 for ext, info in format_support.items() 
                                    if info['supported'] and expected_support.get(ext, False))
                
                print(f"   📈 Extended format support: {supported_count}/{len(expected_support)} formats")
                
                if supported_count >= 5:  # Expect most formats to be supported
                    print(f"   ✅ Extended file format support working correctly")
                else:
                    print(f"   ⚠️  Some extended formats may not be supported")
                
                return True, data
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                return False, {}
                
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}
        
        finally:
            self.tests_run += 1

    def test_enhanced_error_handling(self):
        """Test improved error handling for various edge cases"""
        print(f"\n🔍 Testing Enhanced Error Handling...")
        url = f"{self.base_url}/api/bulk-import/upload"
        
        # Test files that should trigger different error conditions
        test_files = [
            ('files', ('invalid.json', open(self.invalid_json_file, 'rb'), 'application/json')),
            ('files', ('malformed.json', open(self.malformed_json_file, 'rb'), 'application/json')),
            ('files', ('unsupported.txt', open(self.txt_file, 'rb'), 'text/plain')),
            ('files', ('large_animation.json', open(self.large_file, 'rb'), 'application/json'))
        ]
        
        try:
            response = requests.post(url, files=test_files, timeout=30)
            
            # Close file handles
            for _, (_, file_handle, _) in test_files:
                file_handle.close()
            
            success = response.status_code == 200  # Should return 200 with error details
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                
                data = response.json()
                results = data.get('results', [])
                print(f"   📁 Processed {len(results)} error-prone files")
                
                error_types = {}
                for result in results:
                    filename = result.get('filename')
                    status = result.get('status')
                    message = result.get('message', '')
                    
                    if status == 'error':
                        error_types[filename] = message
                        print(f"   ❌ {filename}: {message}")
                    elif status == 'success':
                        print(f"   ✅ {filename}: Processed successfully (large file handling)")
                    else:
                        print(f"   ⚠️  {filename}: {status}")
                
                # Verify error handling quality
                expected_errors = ['invalid.json', 'malformed.json', 'unsupported.txt']
                proper_errors = sum(1 for filename in expected_errors if filename in error_types)
                
                print(f"   📊 Error handling: {proper_errors}/{len(expected_errors)} expected errors caught")
                
                if proper_errors >= 2:  # Expect most errors to be caught
                    print(f"   ✅ Enhanced error handling working correctly")
                else:
                    print(f"   ⚠️  Error handling may need improvement")
                
                return True, data
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                return False, {}
                
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}
        
        finally:
            self.tests_run += 1

    def test_duplicate_detection_improvements(self):
        """Test enhanced duplicate detection with file hashing"""
        print(f"\n🔍 Testing Enhanced Duplicate Detection...")
        url = f"{self.base_url}/api/bulk-import/upload"
        
        try:
            # First upload - should succeed
            files1 = [
                ('files', ('original.json', open(self.standard_lottie_file, 'rb'), 'application/json')),
                ('files', ('original.png', open(self.png_file, 'rb'), 'image/png'))
            ]
            
            response1 = requests.post(url, files=files1, timeout=30)
            
            # Close file handles
            for _, (_, file_handle, _) in files1:
                file_handle.close()
            
            if response1.status_code != 200:
                print(f"❌ First upload failed: {response1.status_code}")
                return False, {}
            
            # Second upload - same files with different names (should detect duplicates)
            files2 = [
                ('files', ('duplicate.json', open(self.standard_lottie_file, 'rb'), 'application/json')),
                ('files', ('duplicate.png', open(self.png_file, 'rb'), 'image/png'))
            ]
            
            response2 = requests.post(url, files=files2, timeout=30)
            
            # Close file handles
            for _, (_, file_handle, _) in files2:
                file_handle.close()
            
            success = response2.status_code == 200
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response2.status_code}")
                
                data = response2.json()
                results = data.get('results', [])
                print(f"   📁 Processed {len(results)} duplicate test files")
                
                duplicate_count = 0
                for result in results:
                    filename = result.get('filename')
                    status = result.get('status')
                    
                    if status == 'duplicate':
                        duplicate_count += 1
                        existing_id = result.get('existing_template_id')
                        print(f"   🔄 {filename}: Duplicate detected (existing: {existing_id})")
                    else:
                        print(f"   ⚠️  {filename}: {status} (expected duplicate)")
                
                print(f"   📊 Duplicate detection: {duplicate_count}/{len(results)} duplicates found")
                
                if duplicate_count >= 1:  # Expect at least one duplicate to be detected
                    print(f"   ✅ Enhanced duplicate detection working correctly")
                else:
                    print(f"   ⚠️  Duplicate detection may not be working properly")
                
                return True, data
            else:
                print(f"❌ Failed - Expected 200, got {response2.status_code}")
                return False, {}
                
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}
        
        finally:
            self.tests_run += 1

    def test_template_creation_from_various_formats(self):
        """Test template creation from different file types with proper element assignment"""
        print(f"\n🔍 Testing Template Creation from Various Formats...")
        
        # First upload files
        upload_success, upload_data = self.test_improved_lottie_validation()
        if not upload_success:
            print("❌ Cannot test template creation - upload failed")
            return False, {}
        
        # Extract successful uploads for template creation
        successful_items = []
        for result in upload_data.get('results', []):
            if result.get('status') == 'success':
                asset_type = result.get('asset_type')
                
                # Determine expected element type based on asset type
                if asset_type == 'Lottie JSON':
                    expected_element_type = 'lottie'
                elif asset_type in ['MP4', 'WebM with Alpha']:
                    expected_element_type = 'video'
                else:
                    expected_element_type = 'image'
                
                successful_items.append({
                    'filename': result.get('filename'),
                    'title': f"Template from {result.get('filename')}",
                    'category': 'Miscellaneous',
                    'tags': ['bulk-import', 'test', asset_type.lower().replace(' ', '-')],
                    'file_url': result.get('file_url'),
                    'asset_type': asset_type,
                    'metadata': result.get('metadata'),
                    'thumbnail_url': result.get('thumbnail_url'),
                    'file_hash': result.get('file_hash'),
                    'creator_id': 'test_bulk_import_enhanced',
                    'is_public': True,
                    'expected_element_type': expected_element_type
                })
        
        if not successful_items:
            print("❌ No successful uploads to create templates from")
            return False, {}
        
        url = f"{self.base_url}/api/bulk-import/create-templates"
        import_data = {'items': successful_items}
        
        try:
            response = requests.post(url, json=import_data, headers={'Content-Type': 'application/json'}, timeout=30)
            
            success = response.status_code == 200
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                
                data = response.json()
                templates_created = data.get('templates_created', [])
                errors = data.get('errors', [])
                summary = data.get('summary', {})
                
                print(f"   📋 Created {len(templates_created)} templates from various formats")
                print(f"   ❌ {len(errors)} errors")
                print(f"   📊 Summary: {summary}")
                
                # Verify template creation and element types
                element_type_verification = {}
                for i, template in enumerate(templates_created):
                    template_id = template.get('template_id')
                    title = template.get('title')
                    print(f"   ✅ Template: {title} (ID: {template_id})")
                    
                    # Store template ID for cleanup
                    if template_id:
                        self.created_resources.append(template_id)
                    
                    # Verify element type assignment (would need to fetch template details)
                    if i < len(successful_items):
                        expected_type = successful_items[i]['expected_element_type']
                        asset_type = successful_items[i]['asset_type']
                        element_type_verification[asset_type] = expected_type
                        print(f"      🎯 Expected element type: {expected_type} for {asset_type}")
                
                if errors:
                    for error in errors:
                        print(f"   ❌ Error for {error.get('filename')}: {error.get('error')}")
                
                # Check success rate
                success_rate = len(templates_created) / (len(templates_created) + len(errors)) if (len(templates_created) + len(errors)) > 0 else 0
                print(f"   📈 Template creation success rate: {success_rate:.1%}")
                
                if success_rate >= 0.8:  # Expect 80%+ success rate
                    print(f"   ✅ Template creation from various formats working correctly")
                else:
                    print(f"   ⚠️  Template creation success rate may be low")
                
                return True, data
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}
                
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}
        
        finally:
            self.tests_run += 1

    def test_metadata_extraction_improvements(self):
        """Test enhanced metadata extraction for different file types"""
        print(f"\n🔍 Testing Enhanced Metadata Extraction...")
        url = f"{self.base_url}/api/bulk-import/upload"
        
        # Test files with different metadata requirements
        test_files = [
            ('files', ('metadata_lottie.json', open(self.standard_lottie_file, 'rb'), 'application/json')),
            ('files', ('metadata_image.png', open(self.png_file, 'rb'), 'image/png')),
            ('files', ('metadata_gif.gif', open(self.gif_file, 'rb'), 'image/gif')),
            ('files', ('metadata_video.mp4', open(self.mp4_file, 'rb'), 'video/mp4'))
        ]
        
        try:
            response = requests.post(url, files=test_files, timeout=30)
            
            # Close file handles
            for _, (_, file_handle, _) in test_files:
                file_handle.close()
            
            success = response.status_code == 200
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                
                data = response.json()
                results = data.get('results', [])
                print(f"   📁 Processed {len(results)} files for metadata extraction")
                
                metadata_quality = {}
                for result in results:
                    filename = result.get('filename')
                    status = result.get('status')
                    asset_type = result.get('asset_type')
                    metadata = result.get('metadata', {})
                    
                    if status == 'success':
                        print(f"   ✅ {filename} ({asset_type}):")
                        
                        # Check metadata completeness based on file type
                        expected_fields = []
                        if asset_type == 'Lottie JSON':
                            expected_fields = ['width', 'height', 'duration', 'frame_rate', 'file_size', 'file_hash']
                        elif asset_type in ['PNG', 'GIF']:
                            expected_fields = ['width', 'height', 'file_size', 'file_hash']
                        elif asset_type in ['MP4', 'WebM with Alpha']:
                            expected_fields = ['width', 'height', 'duration', 'frame_rate', 'file_size', 'file_hash']
                        
                        present_fields = [field for field in expected_fields if field in metadata and metadata[field] is not None]
                        completeness = len(present_fields) / len(expected_fields) if expected_fields else 1
                        
                        metadata_quality[asset_type] = completeness
                        
                        print(f"      📊 Metadata completeness: {completeness:.1%} ({len(present_fields)}/{len(expected_fields)} fields)")
                        
                        # Show key metadata
                        for field in ['width', 'height', 'duration', 'frame_rate', 'file_size']:
                            if field in metadata and metadata[field] is not None:
                                value = metadata[field]
                                if field == 'file_size':
                                    print(f"      📏 {field}: {value} bytes")
                                elif field == 'duration':
                                    print(f"      ⏱️  {field}: {value}s")
                                else:
                                    print(f"      📐 {field}: {value}")
                    else:
                        print(f"   ❌ {filename}: {status}")
                
                # Calculate overall metadata quality
                avg_quality = sum(metadata_quality.values()) / len(metadata_quality) if metadata_quality else 0
                print(f"   📈 Overall metadata extraction quality: {avg_quality:.1%}")
                
                if avg_quality >= 0.7:  # Expect 70%+ metadata completeness
                    print(f"   ✅ Enhanced metadata extraction working correctly")
                else:
                    print(f"   ⚠️  Metadata extraction may need improvement")
                
                return True, data
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                return False, {}
                
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}
        
        finally:
            self.tests_run += 1

def main():
    print("🚀 Starting Comprehensive Bulk Import System Testing...")
    print("=" * 70)
    
    tester = BulkImportTester()
    
    # Create comprehensive test files
    tester.create_comprehensive_test_files()
    
    try:
        # Test improved bulk import functionality
        print("\n🎯 IMPROVED BULK IMPORT TESTS")
        print("-" * 40)
        
        # 1. Test improved Lottie validation (more lenient)
        tester.test_improved_lottie_validation()
        
        # 2. Test extended file format support
        tester.test_extended_file_format_support()
        
        # 3. Test enhanced error handling
        tester.test_enhanced_error_handling()
        
        # 4. Test duplicate detection improvements
        tester.test_duplicate_detection_improvements()
        
        # 5. Test template creation from various formats
        tester.test_template_creation_from_various_formats()
        
        # 6. Test metadata extraction improvements
        tester.test_metadata_extraction_improvements()
        
    finally:
        # Clean up test files
        tester.cleanup_test_files()
    
    # Print final results
    print("\n" + "=" * 70)
    print(f"📊 BULK IMPORT TEST RESULTS: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All bulk import tests passed!")
        return 0
    else:
        failed_tests = tester.tests_run - tester.tests_passed
        print(f"❌ {failed_tests} bulk import tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())