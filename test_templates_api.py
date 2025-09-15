#!/usr/bin/env python3
"""
Test the templates API to see imported templates
"""
import requests
import json

def test_templates_api():
    """Test the templates API endpoint"""
    print("Testing templates API endpoint...")
    
    try:
        # Test the templates endpoint
        response = requests.get(
            'http://localhost:8001/api/templates',
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            templates = response.json()
            print(f"✅ Templates API working! Found {len(templates)} templates")
            
            for i, template in enumerate(templates):
                print(f"\nTemplate {i+1}:")
                print(f"  ID: {template.get('id')}")
                print(f"  Title: {template.get('title')}")
                print(f"  Preview URL: {template.get('preview_url')}")
                print(f"  File URL: {template.get('file_url')}")
                print(f"  Category: {template.get('category')}")
                print(f"  Tags: {template.get('tags', [])}")
                
        else:
            print(f"❌ Templates API failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_templates_api()
