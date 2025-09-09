#!/usr/bin/env python3
"""
Focused test for Lottie file import and template functionality review.
Tests the specific items mentioned in the review request.
"""

import requests
import json
import sys
from pathlib import Path

class LottieReviewTester:
    def __init__(self, base_url="https://motion-templates-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.issues_found = []
        
    def log_issue(self, severity, description):
        """Log an issue found during testing"""
        self.issues_found.append(f"[{severity}] {description}")
        print(f"   🚨 {severity}: {description}")
    
    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, files=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}" if endpoint else f"{self.base_url}/api/"
        headers = {'Content-Type': 'application/json'} if not files else {}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=15)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, timeout=15)
                else:
                    response = requests.post(url, json=data, headers=headers, timeout=15)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=15)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    return True, response_data
                except:
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                    return False, error_data
                except:
                    print(f"   Error: {response.text}")
                    return False, response.text

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, str(e)

    def test_template_data_retrieval(self):
        """Test 1: Template Data Retrieval for specific template ID"""
        print("\n" + "="*60)
        print("TEST 1: TEMPLATE DATA RETRIEVAL")
        print("="*60)
        
        template_id = "89285f08-6340-46c6-87b3-df517b1638e3"
        success, data = self.run_test(
            f"Get Template {template_id}", 
            "GET", 
            f"templates/{template_id}", 
            200
        )
        
        if success:
            # Verify template data structure
            required_fields = ['id', 'title', 'file_url', 'manifest']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                self.log_issue("CRITICAL", f"Template missing required fields: {missing_fields}")
            else:
                print(f"   ✅ Template has all required fields")
                print(f"   - Title: {data.get('title')}")
                print(f"   - File URL: {data.get('file_url')}")
                
                # Check manifest structure
                manifest = data.get('manifest', {})
                if manifest:
                    print(f"   ✅ Template has manifest data")
                    print(f"   - Manifest keys: {list(manifest.keys())}")
                else:
                    self.log_issue("MEDIUM", "Template manifest is empty or missing")
                
                return data
        else:
            self.log_issue("CRITICAL", f"Cannot retrieve template {template_id}")
            return None

    def test_animation_data_access(self):
        """Test 2: Animation Data Access via /data endpoint"""
        print("\n" + "="*60)
        print("TEST 2: ANIMATION DATA ACCESS")
        print("="*60)
        
        template_id = "89285f08-6340-46c6-87b3-df517b1638e3"
        success, data = self.run_test(
            f"Get Animation Data for {template_id}", 
            "GET", 
            f"templates/{template_id}/data", 
            200
        )
        
        if success:
            # Verify it's valid Lottie JSON
            if isinstance(data, dict):
                print(f"   ✅ Returns valid JSON data")
                
                # Check for required Lottie fields
                required_lottie_fields = ['v', 'fr', 'ip', 'op', 'w', 'h', 'layers']
                missing_lottie_fields = [field for field in required_lottie_fields if field not in data]
                
                if missing_lottie_fields:
                    self.log_issue("CRITICAL", f"Animation data missing Lottie fields: {missing_lottie_fields}")
                else:
                    print(f"   ✅ Valid Lottie JSON structure")
                    print(f"   - Version: {data.get('v')}")
                    print(f"   - Frame Rate: {data.get('fr')}")
                    print(f"   - Dimensions: {data.get('w')}x{data.get('h')}")
                    print(f"   - Duration: {(data.get('op', 0) - data.get('ip', 0)) / data.get('fr', 1):.2f}s")
                    print(f"   - Layers: {len(data.get('layers', []))}")
                
                # Test JSON serializability
                try:
                    json_str = json.dumps(data)
                    json.loads(json_str)
                    print(f"   ✅ JSON is serializable and parseable")
                except Exception as e:
                    self.log_issue("CRITICAL", f"Animation data is not properly serializable: {e}")
                
                return data
            else:
                self.log_issue("CRITICAL", f"Animation data is not JSON: {type(data)}")
                return None
        else:
            self.log_issue("CRITICAL", f"Cannot access animation data for template {template_id}")
            return None

    def test_file_url_access(self):
        """Test 3: File URL Access - verify file URLs are accessible"""
        print("\n" + "="*60)
        print("TEST 3: FILE URL ACCESS")
        print("="*60)
        
        # First get template data to find file URLs
        template_id = "89285f08-6340-46c6-87b3-df517b1638e3"
        success, template_data = self.run_test(
            f"Get Template for File URL Test", 
            "GET", 
            f"templates/{template_id}", 
            200
        )
        
        if success and template_data:
            file_url = template_data.get('file_url')
            if file_url:
                print(f"   📁 Testing file URL: {file_url}")
                
                # Test direct file access
                full_url = f"{self.base_url}{file_url}"
                try:
                    response = requests.get(full_url, timeout=10)
                    if response.status_code == 200:
                        print(f"   ✅ File URL is accessible")
                        
                        # Try to parse as JSON
                        try:
                            file_data = response.json()
                            print(f"   ✅ File contains valid JSON")
                            
                            # Check if it's Lottie JSON
                            if 'v' in file_data and 'layers' in file_data:
                                print(f"   ✅ File contains valid Lottie JSON")
                            else:
                                self.log_issue("MEDIUM", "File doesn't appear to be Lottie JSON format")
                                
                        except Exception as e:
                            self.log_issue("MEDIUM", f"File is not valid JSON: {e}")
                            
                    else:
                        self.log_issue("CRITICAL", f"File URL not accessible: {response.status_code}")
                        
                except Exception as e:
                    self.log_issue("CRITICAL", f"Cannot access file URL: {e}")
            else:
                self.log_issue("CRITICAL", "Template has no file_url")
        else:
            self.log_issue("CRITICAL", "Cannot get template data for file URL test")

    def test_manifest_validation(self):
        """Test 4: Manifest Validation - check for editable elements"""
        print("\n" + "="*60)
        print("TEST 4: MANIFEST VALIDATION")
        print("="*60)
        
        template_id = "89285f08-6340-46c6-87b3-df517b1638e3"
        success, template_data = self.run_test(
            f"Get Template for Manifest Test", 
            "GET", 
            f"templates/{template_id}", 
            200
        )
        
        if success and template_data:
            manifest = template_data.get('manifest', {})
            
            if not manifest:
                self.log_issue("CRITICAL", "Template has no manifest data")
                return
            
            print(f"   📋 Manifest structure: {list(manifest.keys())}")
            
            # Check for editable elements
            editable_found = False
            
            # Check for text elements
            if 'text' in manifest:
                text_elements = manifest['text']
                if text_elements:
                    print(f"   ✅ Found {len(text_elements)} text elements")
                    for i, elem in enumerate(text_elements[:3]):  # Show first 3
                        print(f"     - Text {i+1}: {elem}")
                    editable_found = True
                else:
                    print(f"   ⚠️  No text elements found")
            
            # Check for color elements
            if 'colors' in manifest:
                color_elements = manifest['colors']
                if color_elements:
                    print(f"   ✅ Found {len(color_elements)} color elements")
                    for i, elem in enumerate(color_elements[:3]):  # Show first 3
                        print(f"     - Color {i+1}: {elem}")
                    editable_found = True
                else:
                    print(f"   ⚠️  No color elements found")
            
            # Check for other editable elements
            other_editable = ['images', 'shapes', 'effects']
            for elem_type in other_editable:
                if elem_type in manifest:
                    elements = manifest[elem_type]
                    if elements:
                        print(f"   ✅ Found {len(elements)} {elem_type} elements")
                        editable_found = True
            
            if not editable_found:
                self.log_issue("MEDIUM", "No editable elements found in manifest")
            else:
                print(f"   ✅ Manifest contains editable elements")
                
        else:
            self.log_issue("CRITICAL", "Cannot get template data for manifest test")

    def test_upload_functionality(self):
        """Test 5: Upload Functionality - test template upload endpoints"""
        print("\n" + "="*60)
        print("TEST 5: UPLOAD FUNCTIONALITY")
        print("="*60)
        
        # Create a simple test Lottie file
        test_lottie = {
            "v": "5.7.4",
            "fr": 30,
            "ip": 0,
            "op": 90,
            "w": 800,
            "h": 600,
            "nm": "Test Upload Animation",
            "ddd": 0,
            "assets": [],
            "layers": [
                {
                    "ddd": 0,
                    "ind": 1,
                    "ty": 4,
                    "nm": "Test Layer",
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
                    "op": 90,
                    "st": 0,
                    "bm": 0
                }
            ]
        }
        
        # Save to temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_lottie, f)
            temp_file_path = f.name
        
        try:
            # Test file upload
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('test_lottie.json', f, 'application/json')}
                data = {'source': 'test'}
                
                print(f"   📤 Testing file upload...")
                url = f"{self.base_url}/api/templates/upload"
                
                try:
                    response = requests.post(url, files=files, data=data, timeout=15)
                    
                    if response.status_code == 200:
                        self.tests_passed += 1
                        print(f"   ✅ File upload successful")
                        
                        try:
                            result = response.json()
                            print(f"   - Template ID: {result.get('id')}")
                            print(f"   - Template Name: {result.get('name')}")
                            print(f"   - File URL: {result.get('file_url')}")
                            
                            # Verify the uploaded template can be retrieved
                            if 'id' in result:
                                verify_success, verify_data = self.run_test(
                                    "Verify Uploaded Template",
                                    "GET",
                                    f"templates/{result['id']}",
                                    200
                                )
                                if verify_success:
                                    print(f"   ✅ Uploaded template can be retrieved")
                                else:
                                    self.log_issue("MEDIUM", "Uploaded template cannot be retrieved")
                            
                        except Exception as e:
                            self.log_issue("MEDIUM", f"Upload response parsing error: {e}")
                            
                    else:
                        self.log_issue("CRITICAL", f"File upload failed: {response.status_code}")
                        try:
                            error = response.json()
                            print(f"   Error: {error}")
                        except:
                            print(f"   Error: {response.text}")
                            
                except Exception as e:
                    self.log_issue("CRITICAL", f"Upload request failed: {e}")
                    
        finally:
            # Clean up temp file
            Path(temp_file_path).unlink(missing_ok=True)
            
        # Test URL import
        print(f"\n   🌐 Testing URL import...")
        test_url = "https://assets3.lottiefiles.com/packages/lf20_UJNc2t.json"
        
        url = f"{self.base_url}/api/templates/import-url"
        data = {'url': test_url}
        
        try:
            response = requests.post(url, data=data, timeout=15)
            
            if response.status_code == 200:
                self.tests_passed += 1
                print(f"   ✅ URL import successful")
                
                try:
                    result = response.json()
                    print(f"   - Template ID: {result.get('id')}")
                    print(f"   - Template Name: {result.get('name')}")
                    print(f"   - File URL: {result.get('file_url')}")
                except Exception as e:
                    self.log_issue("MEDIUM", f"URL import response parsing error: {e}")
                    
            else:
                self.log_issue("MEDIUM", f"URL import failed: {response.status_code}")
                try:
                    error = response.json()
                    print(f"   Error: {error}")
                except:
                    print(f"   Error: {response.text}")
                    
        except Exception as e:
            self.log_issue("MEDIUM", f"URL import request failed: {e}")

    def test_dotlottie_player_compatibility(self):
        """Test 6: Verify animation data is compatible with dotLottie player"""
        print("\n" + "="*60)
        print("TEST 6: DOTLOTTIE PLAYER COMPATIBILITY")
        print("="*60)
        
        template_id = "89285f08-6340-46c6-87b3-df517b1638e3"
        success, animation_data = self.run_test(
            f"Get Animation Data for Player Test", 
            "GET", 
            f"templates/{template_id}/data", 
            200
        )
        
        if success and animation_data:
            # Check dotLottie player requirements
            player_requirements = {
                'version': 'v',
                'frame_rate': 'fr', 
                'in_point': 'ip',
                'out_point': 'op',
                'width': 'w',
                'height': 'h',
                'layers': 'layers'
            }
            
            missing_requirements = []
            for req_name, req_field in player_requirements.items():
                if req_field not in animation_data:
                    missing_requirements.append(req_name)
            
            if missing_requirements:
                self.log_issue("CRITICAL", f"Animation missing dotLottie player requirements: {missing_requirements}")
            else:
                print(f"   ✅ Animation meets dotLottie player requirements")
                
                # Check specific values
                version = animation_data.get('v', '')
                if version:
                    print(f"   - Lottie Version: {version}")
                else:
                    self.log_issue("MEDIUM", "Missing Lottie version")
                
                # Check layers structure
                layers = animation_data.get('layers', [])
                if layers:
                    print(f"   - Layers: {len(layers)} found")
                    
                    # Check first layer structure
                    first_layer = layers[0]
                    layer_requirements = ['ty', 'nm', 'ks']
                    missing_layer_fields = [field for field in layer_requirements if field not in first_layer]
                    
                    if missing_layer_fields:
                        self.log_issue("MEDIUM", f"Layer missing fields: {missing_layer_fields}")
                    else:
                        print(f"   ✅ Layer structure looks valid")
                else:
                    self.log_issue("CRITICAL", "Animation has no layers")
        else:
            self.log_issue("CRITICAL", "Cannot get animation data for player compatibility test")

    def run_all_tests(self):
        """Run all review tests"""
        print("🎯 LOTTIE FILE IMPORT AND TEMPLATE FUNCTIONALITY REVIEW")
        print("=" * 80)
        print("Testing specific items from the review request...")
        
        # Run all tests
        template_data = self.test_template_data_retrieval()
        animation_data = self.test_animation_data_access()
        self.test_file_url_access()
        self.test_manifest_validation()
        self.test_upload_functionality()
        self.test_dotlottie_player_compatibility()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 REVIEW TEST RESULTS")
        print("=" * 80)
        
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        if self.issues_found:
            print(f"\n🚨 ISSUES FOUND ({len(self.issues_found)}):")
            for issue in self.issues_found:
                print(f"  {issue}")
        else:
            print(f"\n✅ NO CRITICAL ISSUES FOUND")
        
        # Specific findings for review
        print(f"\n📋 REVIEW FINDINGS:")
        print(f"1. Template Data Retrieval: {'✅ WORKING' if template_data else '❌ FAILED'}")
        print(f"2. Animation Data Access: {'✅ WORKING' if animation_data else '❌ FAILED'}")
        print(f"3. File URL Access: {'✅ TESTED' if self.tests_passed > 0 else '❌ FAILED'}")
        print(f"4. Manifest Validation: {'✅ TESTED' if self.tests_passed > 0 else '❌ FAILED'}")
        print(f"5. Upload Functionality: {'✅ TESTED' if self.tests_passed > 0 else '❌ FAILED'}")
        
        return self.tests_passed == self.tests_run and len(self.issues_found) == 0

def main():
    tester = LottieReviewTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())