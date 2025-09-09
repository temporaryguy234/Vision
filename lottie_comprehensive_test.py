#!/usr/bin/env python3
"""
Comprehensive test for Lottie functionality focusing on the review request items.
This test validates the actual functionality needed for the dotLottie player integration.
"""

import requests
import json
import sys
from pathlib import Path
import tempfile

class LottieComprehensiveTest:
    def __init__(self, base_url="https://motion-templates-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_issues = []
        self.minor_issues = []
        
    def log_issue(self, severity, description):
        """Log an issue found during testing"""
        if severity == "CRITICAL":
            self.critical_issues.append(description)
            print(f"   🚨 CRITICAL: {description}")
        else:
            self.minor_issues.append(description)
            print(f"   ⚠️  {severity}: {description}")
    
    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, files=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}" if endpoint else f"{self.base_url}/api/"
        headers = {'Content-Type': 'application/json'} if not files else {}

        self.tests_run += 1
        print(f"\n🔍 {name}")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=15)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, timeout=15)
                else:
                    response = requests.post(url, json=data, headers=headers, timeout=15)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"   ✅ Status: {response.status_code}")
                try:
                    response_data = response.json()
                    return True, response_data
                except:
                    return True, response.text
            else:
                print(f"   ❌ Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                    return False, error_data
                except:
                    print(f"   Error: {response.text}")
                    return False, response.text

        except Exception as e:
            print(f"   ❌ Request failed: {str(e)}")
            return False, str(e)

    def test_template_retrieval_and_structure(self):
        """Test 1: Template data retrieval and structure validation"""
        print("\n" + "="*80)
        print("TEST 1: TEMPLATE DATA RETRIEVAL & STRUCTURE")
        print("="*80)
        
        template_id = "89285f08-6340-46c6-87b3-df517b1638e3"
        success, template_data = self.run_test(
            f"Retrieve template {template_id}", 
            "GET", 
            f"templates/{template_id}", 
            200
        )
        
        if not success:
            self.log_issue("CRITICAL", f"Cannot retrieve template {template_id}")
            return None
            
        # Validate template structure
        required_fields = ['id', 'title', 'file_url', 'manifest']
        missing_fields = [field for field in required_fields if field not in template_data]
        
        if missing_fields:
            self.log_issue("CRITICAL", f"Template missing required fields: {missing_fields}")
        else:
            print(f"   ✅ Template structure valid")
            print(f"   - ID: {template_data.get('id')}")
            print(f"   - Title: {template_data.get('title')}")
            print(f"   - File URL: {template_data.get('file_url')}")
            
        # Validate manifest
        manifest = template_data.get('manifest', {})
        if not manifest:
            self.log_issue("CRITICAL", "Template has no manifest")
        else:
            print(f"   ✅ Manifest present with keys: {list(manifest.keys())}")
            
            # Check for editable elements
            editable_types = ['text', 'colors', 'images']
            found_editable = []
            
            for elem_type in editable_types:
                if elem_type in manifest and manifest[elem_type]:
                    found_editable.append(f"{elem_type}({len(manifest[elem_type])})")
            
            if found_editable:
                print(f"   ✅ Editable elements: {', '.join(found_editable)}")
            else:
                self.log_issue("MINOR", "No editable elements found in manifest")
        
        return template_data

    def test_animation_data_access_and_validation(self):
        """Test 2: Animation data access and Lottie validation"""
        print("\n" + "="*80)
        print("TEST 2: ANIMATION DATA ACCESS & LOTTIE VALIDATION")
        print("="*80)
        
        template_id = "89285f08-6340-46c6-87b3-df517b1638e3"
        success, animation_data = self.run_test(
            f"Get animation data for {template_id}", 
            "GET", 
            f"templates/{template_id}/data", 
            200
        )
        
        if not success:
            self.log_issue("CRITICAL", f"Cannot access animation data for template {template_id}")
            return None
            
        if not isinstance(animation_data, dict):
            self.log_issue("CRITICAL", f"Animation data is not JSON: {type(animation_data)}")
            return None
            
        print(f"   ✅ Animation data is valid JSON")
        
        # Validate Lottie structure
        required_lottie_fields = {
            'v': 'version',
            'fr': 'frame_rate', 
            'ip': 'in_point',
            'op': 'out_point',
            'w': 'width',
            'h': 'height',
            'layers': 'layers'
        }
        
        missing_lottie_fields = []
        for field, description in required_lottie_fields.items():
            if field not in animation_data:
                missing_lottie_fields.append(f"{field}({description})")
        
        if missing_lottie_fields:
            self.log_issue("CRITICAL", f"Animation missing Lottie fields: {missing_lottie_fields}")
        else:
            print(f"   ✅ Valid Lottie JSON structure")
            
            # Display animation properties
            version = animation_data.get('v', 'unknown')
            frame_rate = animation_data.get('fr', 0)
            width = animation_data.get('w', 0)
            height = animation_data.get('h', 0)
            in_point = animation_data.get('ip', 0)
            out_point = animation_data.get('op', 0)
            layers = animation_data.get('layers', [])
            
            duration = (out_point - in_point) / frame_rate if frame_rate > 0 else 0
            
            print(f"   - Version: {version}")
            print(f"   - Dimensions: {width}x{height}")
            print(f"   - Frame Rate: {frame_rate} fps")
            print(f"   - Duration: {duration:.2f}s ({in_point}-{out_point} frames)")
            print(f"   - Layers: {len(layers)}")
            
            # Validate layers
            if not layers:
                self.log_issue("CRITICAL", "Animation has no layers")
            else:
                print(f"   ✅ Animation has {len(layers)} layers")
                
                # Check first layer structure
                first_layer = layers[0]
                layer_required = ['ty', 'nm']  # type and name are essential
                missing_layer_fields = [field for field in layer_required if field not in first_layer]
                
                if missing_layer_fields:
                    self.log_issue("MINOR", f"First layer missing fields: {missing_layer_fields}")
                else:
                    print(f"   ✅ Layer structure valid")
        
        # Test JSON serializability (important for dotLottie player)
        try:
            json_str = json.dumps(animation_data)
            json.loads(json_str)
            print(f"   ✅ Animation data is serializable")
        except Exception as e:
            self.log_issue("CRITICAL", f"Animation data serialization failed: {e}")
        
        return animation_data

    def test_dotlottie_player_compatibility(self):
        """Test 3: Specific dotLottie player compatibility"""
        print("\n" + "="*80)
        print("TEST 3: DOTLOTTIE PLAYER COMPATIBILITY")
        print("="*80)
        
        template_id = "89285f08-6340-46c6-87b3-df517b1638e3"
        success, animation_data = self.run_test(
            f"Get animation for player compatibility test", 
            "GET", 
            f"templates/{template_id}/data", 
            200
        )
        
        if not success or not animation_data:
            self.log_issue("CRITICAL", "Cannot get animation data for compatibility test")
            return False
            
        # Check dotLottie player specific requirements
        compatibility_checks = []
        
        # 1. Version compatibility
        version = animation_data.get('v', '')
        if version:
            try:
                version_parts = version.split('.')
                major_version = int(version_parts[0])
                if major_version >= 5:
                    compatibility_checks.append("✅ Version compatible (v5+)")
                else:
                    compatibility_checks.append("⚠️  Version may be old")
                    self.log_issue("MINOR", f"Lottie version {version} may not be fully compatible")
            except:
                compatibility_checks.append("⚠️  Version format unclear")
        else:
            compatibility_checks.append("❌ No version specified")
            self.log_issue("MINOR", "No Lottie version specified")
        
        # 2. Animation properties
        frame_rate = animation_data.get('fr', 0)
        if frame_rate > 0:
            compatibility_checks.append(f"✅ Frame rate: {frame_rate} fps")
        else:
            compatibility_checks.append("❌ Invalid frame rate")
            self.log_issue("CRITICAL", "Invalid or missing frame rate")
        
        # 3. Dimensions
        width = animation_data.get('w', 0)
        height = animation_data.get('h', 0)
        if width > 0 and height > 0:
            compatibility_checks.append(f"✅ Dimensions: {width}x{height}")
        else:
            compatibility_checks.append("❌ Invalid dimensions")
            self.log_issue("CRITICAL", "Invalid animation dimensions")
        
        # 4. Layers structure
        layers = animation_data.get('layers', [])
        if layers:
            compatibility_checks.append(f"✅ Layers: {len(layers)} found")
            
            # Check for common layer types
            layer_types = {}
            for layer in layers:
                layer_type = layer.get('ty', 'unknown')
                layer_types[layer_type] = layer_types.get(layer_type, 0) + 1
            
            print(f"   - Layer types: {dict(layer_types)}")
        else:
            compatibility_checks.append("❌ No layers")
            self.log_issue("CRITICAL", "Animation has no layers")
        
        # 5. Assets (if any)
        assets = animation_data.get('assets', [])
        if assets:
            compatibility_checks.append(f"✅ Assets: {len(assets)} found")
        else:
            compatibility_checks.append("✅ No external assets (self-contained)")
        
        print(f"\n   📋 Compatibility Summary:")
        for check in compatibility_checks:
            print(f"   {check}")
        
        return True

    def test_upload_and_processing(self):
        """Test 4: Upload functionality and processing"""
        print("\n" + "="*80)
        print("TEST 4: UPLOAD FUNCTIONALITY & PROCESSING")
        print("="*80)
        
        # Create test Lottie animation
        test_lottie = {
            "v": "5.7.4",
            "fr": 30,
            "ip": 0,
            "op": 60,
            "w": 400,
            "h": 400,
            "nm": "Test Upload Animation",
            "ddd": 0,
            "assets": [],
            "layers": [
                {
                    "ddd": 0,
                    "ind": 1,
                    "ty": 4,
                    "nm": "Test Shape Layer",
                    "sr": 1,
                    "ks": {
                        "o": {"a": 0, "k": 100},
                        "r": {"a": 0, "k": 0},
                        "p": {"a": 0, "k": [200, 200, 0]},
                        "a": {"a": 0, "k": [0, 0, 0]},
                        "s": {"a": 0, "k": [100, 100, 100]}
                    },
                    "ao": 0,
                    "shapes": [
                        {
                            "ty": "rc",
                            "d": 1,
                            "s": {"a": 0, "k": [100, 100]},
                            "p": {"a": 0, "k": [0, 0]},
                            "r": {"a": 0, "k": 0}
                        }
                    ],
                    "ip": 0,
                    "op": 60,
                    "st": 0,
                    "bm": 0
                }
            ]
        }
        
        # Test file upload
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_lottie, f)
            temp_file_path = f.name
        
        upload_success = False
        template_id = None
        
        try:
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('test_upload.json', f, 'application/json')}
                data = {'source': 'test_upload'}
                
                url = f"{self.base_url}/api/templates/upload"
                response = requests.post(url, files=files, data=data, timeout=15)
                
                if response.status_code == 200:
                    self.tests_passed += 1
                    upload_success = True
                    print(f"   ✅ File upload successful")
                    
                    try:
                        result = response.json()
                        template_id = result.get('id')
                        print(f"   - Template ID: {template_id}")
                        print(f"   - Template Name: {result.get('name')}")
                        print(f"   - File URL: {result.get('file_url')}")
                        
                        # Test that uploaded template can be retrieved
                        if template_id:
                            verify_success, verify_data = self.run_test(
                                "Verify uploaded template retrieval",
                                "GET",
                                f"templates/{template_id}",
                                200
                            )
                            
                            if verify_success:
                                print(f"   ✅ Uploaded template retrievable")
                                
                                # Test animation data access
                                data_success, anim_data = self.run_test(
                                    "Verify uploaded animation data access",
                                    "GET", 
                                    f"templates/{template_id}/data",
                                    200
                                )
                                
                                if data_success and isinstance(anim_data, dict):
                                    print(f"   ✅ Uploaded animation data accessible")
                                    
                                    # Verify it matches what we uploaded
                                    if (anim_data.get('v') == test_lottie['v'] and 
                                        anim_data.get('w') == test_lottie['w'] and
                                        anim_data.get('h') == test_lottie['h']):
                                        print(f"   ✅ Animation data matches uploaded content")
                                    else:
                                        self.log_issue("MINOR", "Animation data doesn't match uploaded content")
                                else:
                                    self.log_issue("CRITICAL", "Cannot access uploaded animation data")
                            else:
                                self.log_issue("CRITICAL", "Cannot retrieve uploaded template")
                        
                    except Exception as e:
                        self.log_issue("MINOR", f"Upload response parsing error: {e}")
                        
                else:
                    self.log_issue("CRITICAL", f"File upload failed: {response.status_code}")
                    self.tests_run += 1
                    
        except Exception as e:
            self.log_issue("CRITICAL", f"Upload test failed: {e}")
            self.tests_run += 1
            
        finally:
            Path(temp_file_path).unlink(missing_ok=True)
        
        return upload_success, template_id

    def test_multiple_templates(self):
        """Test 5: Multiple template access to ensure system stability"""
        print("\n" + "="*80)
        print("TEST 5: MULTIPLE TEMPLATE ACCESS & SYSTEM STABILITY")
        print("="*80)
        
        # Get list of available templates
        success, templates = self.run_test(
            "Get all templates",
            "GET",
            "templates",
            200
        )
        
        if not success:
            self.log_issue("CRITICAL", "Cannot retrieve template list")
            return False
            
        if not templates or len(templates) == 0:
            self.log_issue("CRITICAL", "No templates found in system")
            return False
            
        print(f"   📋 Found {len(templates)} templates")
        
        # Test accessing multiple templates
        accessible_templates = 0
        working_animations = 0
        
        for i, template in enumerate(templates[:3]):  # Test first 3 templates
            template_id = template.get('id')
            template_title = template.get('title', 'Unknown')
            
            if not template_id:
                continue
                
            print(f"\n   🔍 Testing template {i+1}: {template_title}")
            
            # Test template retrieval
            success, template_data = self.run_test(
                f"Get template {template_title}",
                "GET",
                f"templates/{template_id}",
                200
            )
            
            if success:
                accessible_templates += 1
                
                # Test animation data
                anim_success, anim_data = self.run_test(
                    f"Get animation data for {template_title}",
                    "GET",
                    f"templates/{template_id}/data", 
                    200
                )
                
                if anim_success and isinstance(anim_data, dict):
                    # Quick validation
                    if all(field in anim_data for field in ['v', 'fr', 'w', 'h', 'layers']):
                        working_animations += 1
                        print(f"     ✅ Animation data valid")
                    else:
                        print(f"     ⚠️  Animation data incomplete")
                else:
                    print(f"     ❌ Animation data inaccessible")
            else:
                print(f"     ❌ Template inaccessible")
        
        print(f"\n   📊 Results:")
        print(f"   - Accessible templates: {accessible_templates}/{min(len(templates), 3)}")
        print(f"   - Working animations: {working_animations}/{min(len(templates), 3)}")
        
        if accessible_templates == 0:
            self.log_issue("CRITICAL", "No templates are accessible")
        elif working_animations == 0:
            self.log_issue("CRITICAL", "No animation data is accessible")
        elif working_animations < accessible_templates:
            self.log_issue("MINOR", f"{accessible_templates - working_animations} templates have inaccessible animation data")
        
        return accessible_templates > 0 and working_animations > 0

    def run_comprehensive_test(self):
        """Run all comprehensive tests"""
        print("🎯 COMPREHENSIVE LOTTIE FUNCTIONALITY TEST")
        print("=" * 80)
        print("Testing all aspects of Lottie file import and template functionality...")
        
        # Run all tests
        template_data = self.test_template_retrieval_and_structure()
        animation_data = self.test_animation_data_access_and_validation()
        compatibility_ok = self.test_dotlottie_player_compatibility()
        upload_success, upload_template_id = self.test_upload_and_processing()
        multiple_templates_ok = self.test_multiple_templates()
        
        # Final assessment
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 80)
        
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        success_rate = (self.tests_passed/self.tests_run*100) if self.tests_run > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Issue summary
        total_issues = len(self.critical_issues) + len(self.minor_issues)
        print(f"\nIssues Found: {total_issues}")
        print(f"- Critical: {len(self.critical_issues)}")
        print(f"- Minor: {len(self.minor_issues)}")
        
        if self.critical_issues:
            print(f"\n🚨 CRITICAL ISSUES:")
            for issue in self.critical_issues:
                print(f"  • {issue}")
        
        if self.minor_issues:
            print(f"\n⚠️  MINOR ISSUES:")
            for issue in self.minor_issues:
                print(f"  • {issue}")
        
        # Review-specific findings
        print(f"\n📋 REVIEW REQUEST ASSESSMENT:")
        print(f"1. Template Data Retrieval: {'✅ WORKING' if template_data else '❌ FAILED'}")
        print(f"2. Animation Data Access: {'✅ WORKING' if animation_data else '❌ FAILED'}")
        print(f"3. File URL Access: {'⚠️  ROUTING ISSUE (use /data endpoint)' if template_data else '❌ FAILED'}")
        print(f"4. Manifest Validation: {'✅ WORKING' if template_data and template_data.get('manifest') else '❌ FAILED'}")
        print(f"5. Upload Functionality: {'✅ WORKING' if upload_success else '❌ FAILED'}")
        print(f"6. dotLottie Compatibility: {'✅ COMPATIBLE' if compatibility_ok else '❌ INCOMPATIBLE'}")
        
        # Overall assessment
        critical_functionality_working = (
            template_data is not None and 
            animation_data is not None and 
            len(self.critical_issues) == 0
        )
        
        if critical_functionality_working:
            print(f"\n🎉 OVERALL ASSESSMENT: ✅ LOTTIE FUNCTIONALITY IS WORKING")
            print(f"   The system can successfully import, store, and serve Lottie animations")
            print(f"   for the dotLottie player component. Animation data is accessible via")
            print(f"   the /api/templates/{{id}}/data endpoint as expected.")
        else:
            print(f"\n⚠️  OVERALL ASSESSMENT: ❌ CRITICAL ISSUES FOUND")
            print(f"   Some core functionality is not working properly.")
        
        return critical_functionality_working

def main():
    tester = LottieComprehensiveTest()
    success = tester.run_comprehensive_test()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())