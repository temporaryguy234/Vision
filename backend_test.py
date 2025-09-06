import requests
import sys
import json
from datetime import datetime
import uuid
import os
import tempfile
from pathlib import Path

class MotionEditAPITester:
    def __init__(self, base_url="https://motion-templates-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.created_resources = []

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)

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

    def test_root_endpoint(self):
        """Test API root endpoint"""
        return self.run_test("API Root", "GET", "", 200)

    def test_get_stats(self):
        """Test platform statistics endpoint"""
        success, data = self.run_test("Platform Statistics", "GET", "stats", 200)
        if success:
            expected_keys = ['templates', 'projects', 'exports', 'active_creators', 'time_saved', 'avg_edit_time']
            missing_keys = [key for key in expected_keys if key not in data]
            if missing_keys:
                print(f"   ⚠️  Missing stats keys: {missing_keys}")
            else:
                print(f"   📊 Stats: {data}")
        return success

    def test_get_templates(self):
        """Test getting templates"""
        success, data = self.run_test("Get Templates", "GET", "templates", 200)
        if success:
            print(f"   📋 Found {len(data)} templates")
            if len(data) > 0:
                template = data[0]
                required_fields = ['id', 'title', 'description', 'category', 'preview']
                missing_fields = [field for field in required_fields if field not in template]
                if missing_fields:
                    print(f"   ⚠️  Template missing fields: {missing_fields}")
        return success

    def test_search_templates(self):
        """Test template search functionality"""
        return self.run_test("Search Templates (chart)", "GET", "templates", 200, params={"search": "chart"})

    def test_filter_templates_by_category(self):
        """Test template filtering by category"""
        return self.run_test("Filter Templates (Charts & Maps)", "GET", "templates", 200, 
                           params={"category": "Charts & Maps"})

    def test_create_template(self):
        """Test creating a new template"""
        template_data = {
            "title": f"Test Template {datetime.now().strftime('%H%M%S')}",
            "description": "A test template for API testing",
            "category": "Miscellaneous",
            "preview": "https://placeholder.com/300x200",
            "tags": ["test", "api"],
            "duration": "10s",
            "is_public": True,
            "template_data": {"test": True}
        }
        return self.run_test("Create Template", "POST", "templates", 201, data=template_data)

    def test_get_template_by_id(self, template_id):
        """Test getting a specific template"""
        return self.run_test(f"Get Template {template_id}", "GET", f"templates/{template_id}", 200)

    def test_create_project(self):
        """Test creating a new project"""
        project_data = {
            "title": f"Test Project {datetime.now().strftime('%H%M%S')}",
            "template_id": str(uuid.uuid4()),
            "template_title": "Test Template",
            "thumbnail": "https://placeholder.com/300x200",
            "status": "Draft",
            "duration": "15s",
            "user_id": "test_user_123",
            "project_data": {"test": True}
        }
        return self.run_test("Create Project", "POST", "projects", 201, data=project_data)

    def test_get_projects(self):
        """Test getting projects for a user"""
        return self.run_test("Get Projects", "GET", "projects", 200, params={"user_id": "test_user_123"})

    def test_natural_language_commands(self):
        """Test natural language command parsing"""
        commands = [
            {
                "command": "change color to blue",
                "project_id": str(uuid.uuid4()),
                "element_id": "text_element_1"
            },
            {
                "command": "make text bigger",
                "project_id": str(uuid.uuid4()),
                "element_id": "text_element_2"
            },
            {
                "command": 'change text to "Hello World"',
                "project_id": str(uuid.uuid4()),
                "element_id": "text_element_3"
            }
        ]
        
        results = []
        for i, cmd in enumerate(commands):
            success, data = self.run_test(f"NL Command {i+1}: {cmd['command']}", "POST", "commands/parse", 200, data=cmd)
            results.append(success)
            if success and data.get('success'):
                print(f"   🎯 Command result: {data.get('message')}")
            elif success:
                print(f"   ⚠️  Command not recognized: {data.get('message')}")
        
        return all(results)

    def test_create_export(self):
        """Test creating an export job"""
        export_data = {
            "project_id": str(uuid.uuid4()),
            "project_name": "Test Export Project",
            "format": "MP4",
            "resolution": "1920x1080",
            "user_id": "test_user_123"
        }
        return self.run_test("Create Export", "POST", "exports", 201, data=export_data)

    def test_get_exports(self):
        """Test getting exports for a user"""
        return self.run_test("Get Exports", "GET", "exports", 200, params={"user_id": "test_user_123"})

    def test_create_brand_kit(self):
        """Test creating a brand kit"""
        brand_kit_data = {
            "name": f"Test Brand Kit {datetime.now().strftime('%H%M%S')}",
            "description": "A test brand kit for API testing",
            "colors": ["#FF0000", "#00FF00", "#0000FF"],
            "fonts": ["Arial", "Helvetica", "Times New Roman"],
            "user_id": "test_user_123"
        }
        return self.run_test("Create Brand Kit", "POST", "brand-kits", 201, data=brand_kit_data)

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
        
        # Create a text file (unsupported format)
        self.txt_file = self.test_files_dir / "unsupported.txt"
        with open(self.txt_file, 'w') as f:
            f.write("This is an unsupported file format")
        
        print(f"✅ Created test files in {self.test_files_dir}")

    def cleanup_test_files(self):
        """Clean up test files"""
        import shutil
        if hasattr(self, 'test_files_dir') and self.test_files_dir.exists():
            shutil.rmtree(self.test_files_dir)
            print("✅ Cleaned up test files")

    def test_bulk_import_upload_valid_files(self):
        """Test bulk import upload with valid files"""
        print(f"\n🔍 Testing Bulk Import Upload (Valid Files)...")
        url = f"{self.base_url}/api/bulk-import/upload"
        
        try:
            files = [
                ('files', ('test_animation.json', open(self.lottie_file, 'rb'), 'application/json')),
                ('files', ('test_image.png', open(self.png_file, 'rb'), 'image/png'))
            ]
            
            response = requests.post(url, files=files, timeout=30)
            
            # Close file handles
            for _, (_, file_handle, _) in files:
                file_handle.close()
            
            success = response.status_code == 200
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                
                data = response.json()
                results = data.get('results', [])
                print(f"   📁 Processed {len(results)} files")
                
                for result in results:
                    filename = result.get('filename')
                    status = result.get('status')
                    asset_type = result.get('asset_type')
                    print(f"   - {filename}: {status} ({asset_type})")
                    
                    if status == 'success':
                        # Verify required fields
                        required_fields = ['file_url', 'asset_type', 'metadata', 'file_hash']
                        missing_fields = [field for field in required_fields if field not in result]
                        if missing_fields:
                            print(f"     ⚠️  Missing fields: {missing_fields}")
                        else:
                            print(f"     ✅ All required fields present")
                            
                            # Check metadata for Lottie files
                            if asset_type == 'Lottie JSON':
                                metadata = result.get('metadata', {})
                                lottie_fields = ['width', 'height', 'duration', 'frame_rate']
                                for field in lottie_fields:
                                    if field in metadata:
                                        print(f"     📊 {field}: {metadata[field]}")
                
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

    def test_bulk_import_upload_invalid_files(self):
        """Test bulk import upload with invalid files"""
        print(f"\n🔍 Testing Bulk Import Upload (Invalid Files)...")
        url = f"{self.base_url}/api/bulk-import/upload"
        
        try:
            files = [
                ('files', ('invalid.json', open(self.invalid_json_file, 'rb'), 'application/json')),
                ('files', ('unsupported.txt', open(self.txt_file, 'rb'), 'text/plain'))
            ]
            
            response = requests.post(url, files=files, timeout=30)
            
            # Close file handles
            for _, (_, file_handle, _) in files:
                file_handle.close()
            
            success = response.status_code == 200  # Should still return 200 with error details
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                
                data = response.json()
                results = data.get('results', [])
                print(f"   📁 Processed {len(results)} files")
                
                error_count = 0
                for result in results:
                    filename = result.get('filename')
                    status = result.get('status')
                    message = result.get('message', '')
                    print(f"   - {filename}: {status} - {message}")
                    
                    if status == 'error':
                        error_count += 1
                
                print(f"   ❌ {error_count} files failed as expected")
                return True, data
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                return False, {}
                
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}
        
        finally:
            self.tests_run += 1

    def test_bulk_import_duplicate_detection(self):
        """Test duplicate file detection in bulk import"""
        print(f"\n🔍 Testing Bulk Import Duplicate Detection...")
        url = f"{self.base_url}/api/bulk-import/upload"
        
        try:
            # Upload the same file twice
            files = [
                ('files', ('test_animation_1.json', open(self.lottie_file, 'rb'), 'application/json')),
                ('files', ('test_animation_2.json', open(self.lottie_file, 'rb'), 'application/json'))
            ]
            
            response = requests.post(url, files=files, timeout=30)
            
            # Close file handles
            for _, (_, file_handle, _) in files:
                file_handle.close()
            
            success = response.status_code == 200
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                
                data = response.json()
                results = data.get('results', [])
                
                # First file should succeed, second should be marked as duplicate
                if len(results) >= 2:
                    first_result = results[0]
                    second_result = results[1]
                    
                    print(f"   - First file: {first_result.get('status')}")
                    print(f"   - Second file: {second_result.get('status')}")
                    
                    if (first_result.get('status') == 'success' and 
                        second_result.get('status') == 'duplicate'):
                        print(f"   ✅ Duplicate detection working correctly")
                    else:
                        print(f"   ⚠️  Duplicate detection may not be working as expected")
                
                return True, data
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                return False, {}
                
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}
        
        finally:
            self.tests_run += 1

    def test_bulk_import_create_templates(self):
        """Test creating templates from bulk import data"""
        print(f"\n🔍 Testing Bulk Import Create Templates...")
        
        # First upload some files to get the data
        upload_success, upload_data = self.test_bulk_import_upload_valid_files()
        if not upload_success:
            print("❌ Cannot test template creation - upload failed")
            return False, {}
        
        # Extract successful uploads for template creation
        successful_items = []
        for result in upload_data.get('results', []):
            if result.get('status') == 'success':
                successful_items.append({
                    'filename': result.get('filename'),
                    'title': f"Template from {result.get('filename')}",
                    'category': 'MISCELLANEOUS',
                    'tags': ['bulk-import', 'test'],
                    'file_url': result.get('file_url'),
                    'asset_type': result.get('asset_type'),
                    'metadata': result.get('metadata'),
                    'thumbnail_url': result.get('thumbnail_url'),
                    'file_hash': result.get('file_hash'),
                    'creator_id': 'test_user_bulk_import',
                    'is_public': True
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
                
                print(f"   📋 Created {len(templates_created)} templates")
                print(f"   ❌ {len(errors)} errors")
                print(f"   📊 Summary: {summary}")
                
                for template in templates_created:
                    print(f"   - Template: {template.get('title')} (ID: {template.get('template_id')})")
                    # Store template ID for cleanup
                    if 'template_id' in template:
                        self.created_resources.append(template['template_id'])
                
                if errors:
                    for error in errors:
                        print(f"   ❌ Error for {error.get('filename')}: {error.get('error')}")
                
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

    def test_lottie_element_validation(self):
        """Test LOTTIE element type validation"""
        print(f"\n🔍 Testing LOTTIE Element Validation...")
        
        # Create a template with LOTTIE element
        template_data = {
            "title": f"Lottie Test Template {datetime.now().strftime('%H%M%S')}",
            "category": "MISCELLANEOUS",
            "tags": ["lottie", "test"],
            "preview_image_url": "https://placeholder.com/300x200",
            "creator_id": "test_lottie_validation",
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
                        "id": "lottie_test_element",
                        "type": "lottie",
                        "name": "Test Lottie Animation",
                        "parameters": {
                            "source_url": "/uploads/lottie/test_animation.json",
                            "loop": True,
                            "autoplay": True,
                            "speed": 1.5,
                            "opacity": 0.8,
                            "x": 50.0,
                            "y": 50.0,
                            "scale": 1.2,
                            "rotation": 45.0
                        }
                    }
                ]
            }
        }
        
        return self.run_test("Create Template with LOTTIE Element", "POST", "templates", 201, data=template_data)

    def test_lottie_element_invalid_parameters(self):
        """Test LOTTIE element with invalid parameters"""
        print(f"\n🔍 Testing LOTTIE Element Invalid Parameters...")
        
        # Create a template with invalid LOTTIE element parameters
        template_data = {
            "title": f"Invalid Lottie Test {datetime.now().strftime('%H%M%S')}",
            "category": "MISCELLANEOUS",
            "tags": ["lottie", "test", "invalid"],
            "preview_image_url": "https://placeholder.com/300x200",
            "creator_id": "test_lottie_invalid",
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
                        "id": "invalid_lottie_element",
                        "type": "lottie",
                        "name": "Invalid Lottie Animation",
                        "parameters": {
                            "source_url": "/uploads/lottie/test_animation.json",
                            "loop": True,
                            "autoplay": True,
                            "speed": 10.0,  # Invalid: exceeds max of 5.0
                            "opacity": 2.0,  # Invalid: exceeds max of 1.0
                            "x": 150.0,  # Invalid: exceeds max of 100.0
                            "y": 50.0,
                            "scale": 1.0,
                            "rotation": 0.0
                        }
                    }
                ]
            }
        }
        
        # This should fail with validation errors
        success, data = self.run_test("Create Template with Invalid LOTTIE Parameters", "POST", "templates", 400, data=template_data)
        
        if success and isinstance(data, dict) and 'errors' in data.get('detail', {}):
            errors = data['detail']['errors']
            print(f"   ✅ Validation errors detected: {list(errors.keys())}")
            
            # Check for expected validation errors
            expected_errors = ['elements[0].speed', 'elements[0].opacity', 'elements[0].x']
            found_errors = [error for error in expected_errors if any(error in key for key in errors.keys())]
            
            if found_errors:
                print(f"   ✅ Found expected validation errors: {found_errors}")
            else:
                print(f"   ⚠️  Expected validation errors not found")
        
        return success

    def test_get_brand_kits(self):
        """Test getting brand kits for a user"""
        return self.run_test("Get Brand Kits", "GET", "brand-kits", 200, params={"user_id": "test_user_123"})

def main():
    print("🚀 Starting MotionEdit API Testing...")
    print("=" * 60)
    
    tester = MotionEditAPITester()
    
    # Create test files for bulk import testing
    tester.create_test_files()
    
    try:
        # Test basic endpoints
        print("\n📡 BASIC API TESTS")
        print("-" * 30)
        tester.test_root_endpoint()
        tester.test_get_stats()
        
        # Test template endpoints
        print("\n📋 TEMPLATE TESTS")
        print("-" * 30)
        tester.test_get_templates()
        tester.test_search_templates()
        tester.test_filter_templates_by_category()
        
        # Create a template and test retrieval
        success, template_data = tester.test_create_template()
        if success and 'id' in template_data:
            tester.test_get_template_by_id(template_data['id'])
        
        # Test LOTTIE element validation
        print("\n🎭 LOTTIE ELEMENT TESTS")
        print("-" * 30)
        tester.test_lottie_element_validation()
        tester.test_lottie_element_invalid_parameters()
        
        # Test bulk import functionality
        print("\n📦 BULK IMPORT TESTS")
        print("-" * 30)
        tester.test_bulk_import_upload_valid_files()
        tester.test_bulk_import_upload_invalid_files()
        tester.test_bulk_import_duplicate_detection()
        tester.test_bulk_import_create_templates()
        
        # Test project endpoints
        print("\n📁 PROJECT TESTS")
        print("-" * 30)
        tester.test_create_project()
        tester.test_get_projects()
        
        # Test natural language commands
        print("\n🗣️  NATURAL LANGUAGE TESTS")
        print("-" * 30)
        tester.test_natural_language_commands()
        
        # Test export endpoints
        print("\n📤 EXPORT TESTS")
        print("-" * 30)
        tester.test_create_export()
        tester.test_get_exports()
        
        # Test brand kit endpoints
        print("\n🎨 BRAND KIT TESTS")
        print("-" * 30)
        tester.test_create_brand_kit()
        tester.test_get_brand_kits()
        
    finally:
        # Clean up test files
        tester.cleanup_test_files()
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 FINAL RESULTS: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        failed_tests = tester.tests_run - tester.tests_passed
        print(f"❌ {failed_tests} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())