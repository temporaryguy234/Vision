import requests
import sys
import json
from datetime import datetime
import uuid

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

    def test_get_brand_kits(self):
        """Test getting brand kits for a user"""
        return self.run_test("Get Brand Kits", "GET", "brand-kits", 200, params={"user_id": "test_user_123"})

def main():
    print("🚀 Starting MotionEdit API Testing...")
    print("=" * 60)
    
    tester = MotionEditAPITester()
    
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