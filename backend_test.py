import requests
import sys
import json
from datetime import datetime
import uuid
import os
import tempfile
from pathlib import Path

class MotionEditAPITester:
    def __init__(self, base_url="https://motion-templates-2.preview.emergentagent.com"):
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
                    'category': 'Miscellaneous',  # Use the string value, not enum
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
            "category": "Miscellaneous",
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
            "category": "Miscellaneous",
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

    # LottieFiles Integration Tests
    def test_lottiefiles_search_no_params(self):
        """Test LottieFiles search without parameters (curated animations)"""
        success, data = self.run_test("LottieFiles Search (No Params)", "GET", "lottiefiles/search", 200)
        if success:
            results = data.get('results', [])
            print(f"   🎭 Found {len(results)} curated animations")
            if results:
                first_anim = results[0]
                required_fields = ['id', 'name', 'category', 'file_url', 'tags']
                missing_fields = [field for field in required_fields if field not in first_anim]
                if missing_fields:
                    print(f"   ⚠️  Animation missing fields: {missing_fields}")
                else:
                    print(f"   ✅ Animation structure valid: {first_anim['name']} ({first_anim['category']})")
        return success

    def test_lottiefiles_search_with_query(self):
        """Test LottieFiles search with query parameter"""
        success, data = self.run_test("LottieFiles Search (Query: loading)", "GET", "lottiefiles/search", 200, 
                                    params={"query": "loading"})
        if success:
            results = data.get('results', [])
            print(f"   🔍 Found {len(results)} animations matching 'loading'")
            # Verify results contain loading-related animations
            loading_found = any('loading' in anim.get('name', '').lower() or 
                              'loading' in anim.get('tags', []) for anim in results)
            if loading_found:
                print(f"   ✅ Search filtering working correctly")
            else:
                print(f"   ⚠️  Search results may not be properly filtered")
        return success

    def test_lottiefiles_search_with_category(self):
        """Test LottieFiles search with category filter"""
        success, data = self.run_test("LottieFiles Search (Category: business)", "GET", "lottiefiles/search", 200,
                                    params={"category": "business"})
        if success:
            results = data.get('results', [])
            print(f"   📊 Found {len(results)} business animations")
            # Verify all results are in business category
            if results:
                business_only = all(anim.get('category', '').lower() == 'business' for anim in results)
                if business_only:
                    print(f"   ✅ Category filtering working correctly")
                else:
                    print(f"   ⚠️  Category filtering may not be working properly")
        return success

    def test_lottiefiles_categories(self):
        """Test getting LottieFiles categories"""
        success, data = self.run_test("LottieFiles Categories", "GET", "lottiefiles/categories", 200)
        if success:
            print(f"   📂 Found {len(data)} categories")
            if data:
                first_category = data[0]
                required_fields = ['slug', 'name', 'description']
                missing_fields = [field for field in required_fields if field not in first_category]
                if missing_fields:
                    print(f"   ⚠️  Category missing fields: {missing_fields}")
                else:
                    print(f"   ✅ Category structure valid")
                    for category in data[:3]:  # Show first 3 categories
                        print(f"   - {category['name']}: {category['description']}")
        return success

    def test_lottiefiles_popular(self):
        """Test getting popular LottieFiles animations"""
        success, data = self.run_test("LottieFiles Popular", "GET", "lottiefiles/popular", 200)
        if success:
            print(f"   ⭐ Found {len(data)} popular animations")
            if data:
                for anim in data[:2]:  # Show first 2 animations
                    print(f"   - {anim.get('name')} ({anim.get('category')})")
        return success

    def test_lottiefiles_popular_with_category(self):
        """Test getting popular animations with category filter"""
        success, data = self.run_test("LottieFiles Popular (Category: technology)", "GET", "lottiefiles/popular", 200,
                                    params={"category": "technology"})
        if success:
            print(f"   💻 Found {len(data)} popular technology animations")
            if data:
                tech_only = all(anim.get('category', '').lower() == 'technology' for anim in data)
                if tech_only:
                    print(f"   ✅ Category filtering in popular animations working")
                else:
                    print(f"   ⚠️  Category filtering in popular animations may not be working")
        return success

    def test_lottiefiles_animation_details_valid(self):
        """Test getting details for a specific LottieFiles animation"""
        # Use a known animation ID from curated list
        animation_id = "loading_spinner"
        success, data = self.run_test(f"LottieFiles Animation Details ({animation_id})", "GET", 
                                    f"lottiefiles/animation/{animation_id}", 200)
        if success:
            required_fields = ['id', 'name', 'description', 'category', 'file_url', 'dimensions']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                print(f"   ⚠️  Animation details missing fields: {missing_fields}")
            else:
                print(f"   ✅ Animation details complete")
                print(f"   - Name: {data.get('name')}")
                print(f"   - Category: {data.get('category')}")
                print(f"   - Duration: {data.get('duration')}s")
                print(f"   - Dimensions: {data.get('dimensions')}")
        return success

    def test_lottiefiles_animation_details_invalid(self):
        """Test getting details for invalid animation ID"""
        invalid_id = "nonexistent_animation_id"
        success, data = self.run_test(f"LottieFiles Animation Details (Invalid ID)", "GET", 
                                    f"lottiefiles/animation/{invalid_id}", 404)
        if success:
            print(f"   ✅ Properly returns 404 for invalid animation ID")
        return success

    def test_lottiefiles_import_animation(self):
        """Test importing a LottieFiles animation to create template"""
        # Use a known animation ID from curated list
        animation_id = "success_checkmark"
        success, data = self.run_test(f"LottieFiles Import Animation ({animation_id})", "POST", 
                                    f"lottiefiles/import/{animation_id}", 200)
        if success:
            required_fields = ['message', 'template_id', 'template_slug', 'template_title', 'category']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                print(f"   ⚠️  Import response missing fields: {missing_fields}")
            else:
                print(f"   ✅ Animation imported successfully")
                print(f"   - Template ID: {data.get('template_id')}")
                print(f"   - Template Title: {data.get('template_title')}")
                print(f"   - Template Slug: {data.get('template_slug')}")
                print(f"   - Category: {data.get('category')}")
                
                # Store template ID for cleanup
                if 'template_id' in data:
                    self.created_resources.append(data['template_id'])
                
                # Verify the template was actually created by trying to fetch it
                template_id = data.get('template_id')
                if template_id:
                    verify_success, template_data = self.run_test(f"Verify Imported Template", "GET", 
                                                                f"templates/{template_id}", 200)
                    if verify_success:
                        print(f"   ✅ Imported template verified in database")
                        # Check if it has LOTTIE element
                        elements = template_data.get('editable_parameters_schema', {}).get('elements', [])
                        lottie_elements = [elem for elem in elements if elem.get('type') == 'lottie']
                        if lottie_elements:
                            print(f"   ✅ Template contains {len(lottie_elements)} LOTTIE element(s)")
                            lottie_elem = lottie_elements[0]
                            params = lottie_elem.get('parameters', {})
                            print(f"   - Source URL: {params.get('source_url')}")
                            print(f"   - Loop: {params.get('loop')}")
                            print(f"   - Autoplay: {params.get('autoplay')}")
                        else:
                            print(f"   ⚠️  Template missing LOTTIE elements")
                    else:
                        print(f"   ❌ Could not verify imported template in database")
        return success

    def test_lottiefiles_import_invalid_animation(self):
        """Test importing invalid animation ID"""
        invalid_id = "nonexistent_animation_for_import"
        success, data = self.run_test(f"LottieFiles Import Invalid Animation", "POST", 
                                    f"lottiefiles/import/{invalid_id}", 404)
        if success:
            print(f"   ✅ Properly returns 404 for invalid animation import")
        return success

    def test_lottiefiles_import_with_category(self):
        """Test importing animation with target category"""
        animation_id = "business_growth"
        success, data = self.run_test(f"LottieFiles Import with Category", "POST", 
                                    f"lottiefiles/import/{animation_id}", 200,
                                    params={"target_category": "business"})
        if success:
            print(f"   ✅ Animation imported with target category")
            print(f"   - Final Category: {data.get('category')}")
            
            # Store template ID for cleanup
            if 'template_id' in data:
                self.created_resources.append(data['template_id'])
        return success

    def test_lottiefiles_animation_data_endpoint(self):
        """Test the animation data endpoint that returns Lottie JSON"""
        print(f"\n🔍 Testing LottieFiles Animation Data Endpoint...")
        
        # Test with loading_spinner animation ID
        animation_id = "loading_spinner"
        success1, data1 = self.run_test(f"Animation Data ({animation_id})", "GET", 
                                      f"lottiefiles/animation/{animation_id}/data", 200)
        
        if success1:
            # Verify it's valid JSON and not HTML
            if isinstance(data1, dict):
                print(f"   ✅ Returns valid JSON (not HTML)")
                
                # Check for required Lottie JSON structure
                required_lottie_fields = ['v', 'fr', 'ip', 'op', 'w', 'h', 'layers']
                missing_fields = [field for field in required_lottie_fields if field not in data1]
                
                if missing_fields:
                    print(f"   ⚠️  Missing Lottie fields: {missing_fields}")
                else:
                    print(f"   ✅ Valid Lottie JSON structure")
                    print(f"   - Version: {data1.get('v')}")
                    print(f"   - Frame Rate: {data1.get('fr')}")
                    print(f"   - Dimensions: {data1.get('w')}x{data1.get('h')}")
                    print(f"   - Layers: {len(data1.get('layers', []))}")
                
                # Test JSON parseability
                try:
                    json_str = json.dumps(data1)
                    parsed_back = json.loads(json_str)
                    print(f"   ✅ JSON is parseable and serializable")
                except Exception as e:
                    print(f"   ❌ JSON parsing error: {e}")
            else:
                print(f"   ❌ Response is not JSON: {type(data1)}")
                if isinstance(data1, str) and data1.startswith('<!DOCTYPE'):
                    print(f"   ❌ Received HTML instead of JSON")
        
        # Test with success_checkmark animation ID
        animation_id2 = "success_checkmark"
        success2, data2 = self.run_test(f"Animation Data ({animation_id2})", "GET", 
                                      f"lottiefiles/animation/{animation_id2}/data", 200)
        
        if success2:
            if isinstance(data2, dict):
                print(f"   ✅ Second animation also returns valid JSON")
                
                # Verify embedded:// URL handling
                # Check if this animation has embedded data
                required_fields = ['v', 'layers']
                if all(field in data2 for field in required_fields):
                    print(f"   ✅ Embedded:// URL handling works correctly")
                else:
                    print(f"   ⚠️  Embedded data may not be complete")
            else:
                print(f"   ❌ Second animation response is not JSON")
        
        # Test with invalid animation ID
        invalid_id = "nonexistent_animation"
        success3, data3 = self.run_test(f"Animation Data (Invalid ID)", "GET", 
                                      f"lottiefiles/animation/{invalid_id}/data", 404)
        
        if success3:
            print(f"   ✅ Properly returns 404 for invalid animation ID")
        
        return success1 and success2 and success3

    def test_lottiefiles_embedded_url_handling(self):
        """Test that embedded:// URLs are processed correctly"""
        print(f"\n🔍 Testing Embedded URL Handling...")
        
        # First get animation details to see the embedded URL
        animation_id = "loading_spinner"
        success1, details = self.run_test(f"Get Animation Details", "GET", 
                                        f"lottiefiles/animation/{animation_id}", 200)
        
        if success1:
            file_url = details.get('file_url', '')
            if file_url.startswith('embedded://'):
                print(f"   ✅ Animation uses embedded:// URL: {file_url}")
                
                # Now test that the data endpoint processes this correctly
                success2, lottie_data = self.run_test(f"Get Embedded Animation Data", "GET", 
                                                    f"lottiefiles/animation/{animation_id}/data", 200)
                
                if success2 and isinstance(lottie_data, dict):
                    print(f"   ✅ Embedded URL processed correctly")
                    print(f"   - Animation Name: {lottie_data.get('nm', 'Unknown')}")
                    print(f"   - Has Layers: {len(lottie_data.get('layers', []))} layers")
                    return True
                else:
                    print(f"   ❌ Failed to process embedded URL")
                    return False
            else:
                print(f"   ⚠️  Animation doesn't use embedded URL: {file_url}")
                return True
        
        return False

    def test_lottiefiles_import_with_data_verification(self):
        """Test importing animation and verify the template uses correct embedded URL"""
        print(f"\n🔍 Testing Import with Data Verification...")
        
        animation_id = "loading_spinner"
        success1, import_result = self.run_test(f"Import Animation for Data Test", "POST", 
                                              f"lottiefiles/import/{animation_id}", 200)
        
        if success1:
            template_id = import_result.get('template_id')
            if template_id:
                # Store for cleanup
                self.created_resources.append(template_id)
                
                # Get the created template
                success2, template_data = self.run_test(f"Get Imported Template", "GET", 
                                                      f"templates/{template_id}", 200)
                
                if success2:
                    # Check if template has LOTTIE element with embedded URL
                    elements = template_data.get('editable_parameters_schema', {}).get('elements', [])
                    lottie_elements = [elem for elem in elements if elem.get('type') == 'lottie']
                    
                    if lottie_elements:
                        lottie_elem = lottie_elements[0]
                        source_url = lottie_elem.get('parameters', {}).get('source_url', '')
                        
                        if source_url.startswith('embedded://'):
                            print(f"   ✅ Template uses embedded URL: {source_url}")
                            
                            # Test that we can get the data for this embedded URL
                            embedded_id = source_url.replace('embedded://', '')
                            success3, data = self.run_test(f"Verify Embedded Data Access", "GET", 
                                                         f"lottiefiles/animation/{embedded_id}/data", 200)
                            
                            if success3 and isinstance(data, dict):
                                print(f"   ✅ Can access embedded animation data")
                                return True
                            else:
                                print(f"   ❌ Cannot access embedded animation data")
                                return False
                        else:
                            print(f"   ⚠️  Template doesn't use embedded URL: {source_url}")
                            return True
                    else:
                        print(f"   ❌ Template missing LOTTIE elements")
                        return False
                else:
                    print(f"   ❌ Could not retrieve imported template")
                    return False
            else:
                print(f"   ❌ Import didn't return template ID")
                return False
        
        return False

    def test_lottie_upload_endpoints(self):
        """Test the specific Lottie file upload functionality as requested in review"""
        print(f"\n🎯 LOTTIE FILE UPLOAD FUNCTIONALITY TESTING")
        print("-" * 50)
        
        # Test 1: Upload Endpoints Testing - Test /api/templates/upload for Lottie JSON files
        print(f"\n🔍 Testing Lottie JSON File Upload...")
        url = f"{self.base_url}/api/templates/upload"
        
        try:
            files = {'file': ('test_lottie.json', open(self.lottie_file, 'rb'), 'application/json')}
            data = {'source': 'upload'}
            
            response = requests.post(url, files=files, data=data, timeout=30)
            files['file'][1].close()  # Close file handle
            
            success = response.status_code == 200
            if success:
                self.tests_passed += 1
                print(f"✅ Lottie JSON Upload - Status: {response.status_code}")
                
                upload_result = response.json()
                template_id = upload_result.get('id')
                
                # Verify response structure
                required_fields = ['id', 'name', 'preview_url', 'manifest', 'file_url']
                missing_fields = [field for field in required_fields if field not in upload_result]
                if missing_fields:
                    print(f"   ⚠️  Missing response fields: {missing_fields}")
                else:
                    print(f"   ✅ Upload response complete")
                    print(f"   - Template ID: {template_id}")
                    print(f"   - File URL: {upload_result.get('file_url')}")
                    print(f"   - Preview URL: {upload_result.get('preview_url')}")
                    
                    # Store for further testing
                    if template_id:
                        self.created_resources.append(template_id)
                        
                        # Test 2: Template Creation - Verify template was created properly
                        print(f"\n🔍 Testing Template Creation from Upload...")
                        template_success, template_data = self.run_test(
                            f"Get Uploaded Template", "GET", f"templates/{template_id}", 200
                        )
                        
                        if template_success:
                            print(f"   ✅ Template created successfully")
                            print(f"   - Title: {template_data.get('title')}")
                            print(f"   - Category: {template_data.get('category')}")
                            print(f"   - File URL: {template_data.get('file_url')}")
                            
                            # Test 3: Manifest Generation - Check manifest quality
                            manifest = template_data.get('manifest', {})
                            if manifest:
                                print(f"   ✅ Manifest generated")
                                text_elements = len(manifest.get('text', []))
                                color_elements = len(manifest.get('colors', []))
                                image_elements = len(manifest.get('images', []))
                                print(f"   - Text elements: {text_elements}")
                                print(f"   - Color elements: {color_elements}")
                                print(f"   - Image elements: {image_elements}")
                                print(f"   - Speed control: {manifest.get('speed', {})}")
                                print(f"   - Anchors: {len(manifest.get('anchors', []))}")
                            else:
                                print(f"   ⚠️  No manifest generated")
                            
                            # Test 4: File Storage - Verify file is accessible
                            file_url = template_data.get('file_url', '')
                            if file_url:
                                print(f"\n🔍 Testing File Storage Access...")
                                # Try to access the file directly
                                file_access_url = f"{self.base_url}{file_url}"
                                try:
                                    file_response = requests.get(file_access_url, timeout=10)
                                    if file_response.status_code == 200:
                                        print(f"   ✅ File accessible at: {file_url}")
                                        # Verify it's valid JSON
                                        try:
                                            file_json = file_response.json()
                                            if 'v' in file_json and 'layers' in file_json:
                                                print(f"   ✅ File contains valid Lottie JSON")
                                            else:
                                                print(f"   ⚠️  File may not be valid Lottie format")
                                        except:
                                            print(f"   ⚠️  File is not valid JSON")
                                    else:
                                        print(f"   ⚠️  File not accessible directly (Status: {file_response.status_code})")
                                        # This might be expected due to routing - test via data endpoint
                                        print(f"   🔍 Testing via data endpoint instead...")
                                        data_success, data_result = self.run_test(
                                            f"Get Template Data", "GET", f"templates/{template_id}/data", 200
                                        )
                                        if data_success:
                                            print(f"   ✅ Template data accessible via API endpoint")
                                        else:
                                            print(f"   ❌ Template data not accessible")
                                except Exception as e:
                                    print(f"   ❌ File access error: {e}")
                            
                            # Test 5: Library Display - Verify template appears in library
                            print(f"\n🔍 Testing Library Display...")
                            library_success, library_data = self.run_test(
                                f"Get Templates Library", "GET", "templates", 200
                            )
                            
                            if library_success:
                                # Check if our uploaded template appears
                                uploaded_template = None
                                for template in library_data:
                                    if template.get('id') == template_id:
                                        uploaded_template = template
                                        break
                                
                                if uploaded_template:
                                    print(f"   ✅ Template appears in library")
                                    print(f"   - Has preview URL: {'preview_image_url' in uploaded_template}")
                                    print(f"   - Has file URL: {'file_url' in uploaded_template}")
                                    print(f"   - Is public: {uploaded_template.get('is_public', False)}")
                                else:
                                    print(f"   ⚠️  Template not found in library")
                        
                return True, upload_result
            else:
                print(f"❌ Lottie JSON Upload Failed - Expected 200, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}
                
        except Exception as e:
            print(f"❌ Lottie JSON Upload Failed - Error: {str(e)}")
            return False, {}
        
        finally:
            self.tests_run += 1

    def test_lottie_url_import(self):
        """Test importing Lottie files from URL"""
        print(f"\n🔍 Testing Lottie URL Import...")
        
        # Test with a sample Lottie URL (we'll use a mock URL for testing)
        test_url = "https://assets3.lottiefiles.com/packages/lf20_UJNc2t.json"
        
        import_data = {'url': test_url}
        success, result = self.run_test(
            "Import Lottie from URL", "POST", "templates/import-url", 200, data=import_data
        )
        
        if success:
            template_id = result.get('id')
            if template_id:
                self.created_resources.append(template_id)
                print(f"   ✅ URL import successful")
                print(f"   - Template ID: {template_id}")
                print(f"   - File URL: {result.get('file_url')}")
                
                # Verify the imported template
                verify_success, template_data = self.run_test(
                    f"Verify URL Import", "GET", f"templates/{template_id}", 200
                )
                
                if verify_success:
                    print(f"   ✅ Imported template verified")
                    print(f"   - Source: {template_data.get('source')}")
                    print(f"   - Description contains URL: {'URL' in template_data.get('description', '')}")
        
        return success

    def test_lottie_zip_file_upload(self):
        """Test uploading .lottie ZIP files"""
        print(f"\n🔍 Testing .lottie ZIP File Upload...")
        
        # Create a simple .lottie ZIP file for testing
        import zipfile
        import tempfile
        
        # Create a temporary .lottie file
        lottie_zip_path = self.test_files_dir / "test_animation.lottie"
        
        # Create ZIP with our test Lottie JSON
        with zipfile.ZipFile(lottie_zip_path, 'w') as zip_file:
            zip_file.write(self.lottie_file, 'data.json')
        
        url = f"{self.base_url}/api/templates/upload"
        
        try:
            files = {'file': ('test_animation.lottie', open(lottie_zip_path, 'rb'), 'application/zip')}
            data = {'source': 'upload'}
            
            response = requests.post(url, files=files, data=data, timeout=30)
            files['file'][1].close()  # Close file handle
            
            success = response.status_code == 200
            if success:
                self.tests_passed += 1
                print(f"✅ .lottie ZIP Upload - Status: {response.status_code}")
                
                upload_result = response.json()
                template_id = upload_result.get('id')
                
                if template_id:
                    self.created_resources.append(template_id)
                    print(f"   ✅ .lottie file processed successfully")
                    print(f"   - Template ID: {template_id}")
                    
                    # Test that we can get the animation data
                    data_success, animation_data = self.run_test(
                        f"Get .lottie Animation Data", "GET", f"templates/{template_id}/data", 200
                    )
                    
                    if data_success:
                        print(f"   ✅ Animation data extracted from ZIP")
                        print(f"   - Has layers: {'layers' in animation_data}")
                        print(f"   - Version: {animation_data.get('v', 'Unknown')}")
                
                return True, upload_result
            else:
                print(f"❌ .lottie ZIP Upload Failed - Expected 200, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}
                
        except Exception as e:
            print(f"❌ .lottie ZIP Upload Failed - Error: {str(e)}")
            return False, {}
        
        finally:
            self.tests_run += 1

    def test_preview_thumbnail_generation(self):
        """Test if preview images/thumbnails are being generated"""
        print(f"\n🔍 Testing Preview/Thumbnail Generation...")
        
        # Upload a file first
        upload_success, upload_result = self.test_lottie_upload_endpoints()
        
        if upload_success:
            template_id = upload_result.get('id')
            preview_url = upload_result.get('preview_url')
            
            if preview_url:
                print(f"   ✅ Preview URL generated: {preview_url}")
                
                # Try to access the preview
                if preview_url.startswith('/'):
                    full_preview_url = f"{self.base_url}{preview_url}"
                else:
                    full_preview_url = preview_url
                
                try:
                    preview_response = requests.get(full_preview_url, timeout=10)
                    if preview_response.status_code == 200:
                        print(f"   ✅ Preview image accessible")
                        # Check if it's actually an image
                        content_type = preview_response.headers.get('content-type', '')
                        if 'image' in content_type:
                            print(f"   ✅ Preview is valid image ({content_type})")
                        else:
                            print(f"   ⚠️  Preview URL doesn't return image content ({content_type})")
                    else:
                        print(f"   ⚠️  Preview image not accessible (Status: {preview_response.status_code})")
                        print(f"   ℹ️  This might be expected if thumbnails are generated asynchronously")
                except Exception as e:
                    print(f"   ⚠️  Preview access error: {e}")
            else:
                print(f"   ⚠️  No preview URL in upload response")
        else:
            print(f"   ❌ Cannot test preview generation - upload failed")
        
        return upload_success

def main():
    print("🚀 Starting MotionEdit API Testing...")
    print("🎯 FOCUS: Lottie File Upload Functionality Review")
    print("=" * 60)
    
    tester = MotionEditAPITester()
    
    # Create test files for bulk import testing
    tester.create_test_files()
    
    try:
        # Test the specific Lottie upload functionality as requested
        print("\n🎯 LOTTIE FILE UPLOAD FUNCTIONALITY TESTS (REVIEW REQUEST)")
        print("=" * 60)
        
        # 1. Upload Endpoints Testing
        tester.test_lottie_upload_endpoints()
        
        # 2. URL Import Testing  
        tester.test_lottie_url_import()
        
        # 3. .lottie ZIP File Testing
        tester.test_lottie_zip_file_upload()
        
        # 4. Preview/Thumbnail Generation Testing
        tester.test_preview_thumbnail_generation()
        
        # Additional comprehensive tests
        print("\n📋 ADDITIONAL TEMPLATE & LIBRARY TESTS")
        print("-" * 40)
        tester.test_get_templates()
        
        # Test basic endpoints for context
        print("\n📡 BASIC API HEALTH TESTS")
        print("-" * 30)
        tester.test_root_endpoint()
        
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