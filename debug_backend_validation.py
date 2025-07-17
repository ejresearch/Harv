#!/usr/bin/env python3
"""
Debug Backend Validation Requirements
Find out exactly what your backend expects for auth endpoints
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_login_formats():
    """Test different login formats to see what works"""
    print("🔍 Testing Login Endpoint Validation")
    print("====================================")
    
    test_cases = [
        {
            "name": "OAuth2 Form Data (working)",
            "method": "form",
            "data": {
                "username": "questfortheprimer@gmail.com",
                "password": "Joust?poet1c",
                "grant_type": "password"
            }
        },
        {
            "name": "JSON with email",
            "method": "json",
            "data": {
                "email": "questfortheprimer@gmail.com",
                "password": "Joust?poet1c"
            }
        },
        {
            "name": "JSON with username",
            "method": "json",
            "data": {
                "username": "questfortheprimer@gmail.com",
                "password": "Joust?poet1c"
            }
        }
    ]
    
    for case in test_cases:
        print(f"\n🧪 Testing: {case['name']}")
        try:
            if case['method'] == 'form':
                response = requests.post(
                    f"{BASE_URL}/auth/login",
                    data=case['data'],
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
            else:
                response = requests.post(
                    f"{BASE_URL}/auth/login",
                    json=case['data'],
                    headers={"Content-Type": "application/json"}
                )
            
            print(f"   Status: {response.status_code}")
            if response.status_code == 422:
                try:
                    error_detail = response.json()
                    print(f"   Validation Error: {error_detail}")
                except:
                    print(f"   Error: {response.text}")
            elif response.status_code == 200:
                print("   ✅ SUCCESS!")
            else:
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_registration_formats():
    """Test different registration formats"""
    print("\n🔍 Testing Registration Endpoint Validation")
    print("===========================================")
    
    test_cases = [
        {
            "name": "Complete JSON Registration",
            "data": {
                "email": "test@example.com",
                "password": "testpass123",
                "name": "Test User",
                "reason": "Learning",
                "familiarity": "Beginner",
                "learning_style": "Mixed"
            }
        },
        {
            "name": "Minimal JSON Registration",
            "data": {
                "email": "test2@example.com",
                "password": "testpass123"
            }
        },
        {
            "name": "Registration with username field",
            "data": {
                "username": "test3@example.com",
                "email": "test3@example.com", 
                "password": "testpass123",
                "name": "Test User 3"
            }
        }
    ]
    
    for case in test_cases:
        print(f"\n🧪 Testing: {case['name']}")
        try:
            response = requests.post(
                f"{BASE_URL}/auth/register",
                json=case['data'],
                headers={"Content-Type": "application/json"}
            )
            
            print(f"   Status: {response.status_code}")
            if response.status_code == 422:
                try:
                    error_detail = response.json()
                    print(f"   Validation Error: {error_detail}")
                    if 'detail' in error_detail:
                        for error in error_detail['detail']:
                            field = error.get('loc', ['unknown'])[-1]
                            msg = error.get('msg', 'Unknown error')
                            print(f"     - Field '{field}': {msg}")
                except:
                    print(f"   Error: {response.text}")
            elif response.status_code == 200:
                print("   ✅ SUCCESS!")
            else:
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def check_backend_models():
    """Check what the backend API documentation says"""
    print("\n🔍 Checking Backend API Documentation")
    print("====================================")
    
    try:
        # Check OpenAPI docs
        response = requests.get(f"{BASE_URL}/openapi.json")
        if response.status_code == 200:
            api_spec = response.json()
            
            # Look for auth endpoints
            paths = api_spec.get('paths', {})
            
            if '/auth/login' in paths:
                login_spec = paths['/auth/login'].get('post', {})
                print("\n📋 Login endpoint expects:")
                if 'requestBody' in login_spec:
                    content = login_spec['requestBody'].get('content', {})
                    for content_type, schema_info in content.items():
                        print(f"   Content-Type: {content_type}")
                        schema = schema_info.get('schema', {})
                        if 'properties' in schema:
                            print("   Required fields:")
                            for field, field_info in schema['properties'].items():
                                field_type = field_info.get('type', 'unknown')
                                print(f"     - {field}: {field_type}")
            
            if '/auth/register' in paths:
                register_spec = paths['/auth/register'].get('post', {})
                print("\n📋 Register endpoint expects:")
                if 'requestBody' in register_spec:
                    content = register_spec['requestBody'].get('content', {})
                    for content_type, schema_info in content.items():
                        print(f"   Content-Type: {content_type}")
                        schema = schema_info.get('schema', {})
                        if 'properties' in schema:
                            print("   Available fields:")
                            for field, field_info in schema['properties'].items():
                                field_type = field_info.get('type', 'unknown')
                                required = field in schema.get('required', [])
                                status = "REQUIRED" if required else "optional"
                                print(f"     - {field}: {field_type} ({status})")
        else:
            print("   ❌ Could not fetch API documentation")
            
    except Exception as e:
        print(f"   ❌ Error checking API docs: {e}")

def analyze_backend_code():
    """Look at the actual backend code to understand validation"""
    print("\n🔍 Analyzing Backend Code")
    print("========================")
    
    import os
    import glob
    
    # Find auth-related files
    auth_files = []
    for root, dirs, files in os.walk("backend"):
        for file in files:
            if file.endswith('.py') and ('auth' in file.lower() or 'user' in file.lower() or 'models' in file.lower()):
                auth_files.append(os.path.join(root, file))
    
    print("📁 Found auth-related files:")
    for file in auth_files:
        print(f"   - {file}")
        
        # Look for Pydantic models
        try:
            with open(file, 'r') as f:
                content = f.read()
                
            if 'class' in content and ('Request' in content or 'Model' in content):
                print(f"\n📋 Models in {file}:")
                lines = content.split('\n')
                in_class = False
                current_class = ""
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('class ') and ('Request' in line or 'Model' in line or 'User' in line):
                        current_class = line.split('class ')[1].split('(')[0].split(':')[0]
                        in_class = True
                        print(f"   🏷️  {current_class}:")
                    elif in_class and line.startswith('class '):
                        in_class = False
                    elif in_class and ':' in line and not line.startswith('#'):
                        if '=' in line:
                            field_name = line.split(':')[0].strip()
                            field_type = line.split(':')[1].split('=')[0].strip()
                            print(f"     - {field_name}: {field_type}")
                        
        except Exception as e:
            print(f"   ❌ Error reading {file}: {e}")

def main():
    print("🕵️ Backend Validation Detective")
    print("===============================")
    print("Let's figure out exactly what your backend expects!\n")
    
    # Test current authentication
    test_login_formats()
    
    # Test registration
    test_registration_formats()
    
    # Check API documentation
    check_backend_models()
    
    # Analyze backend code
    analyze_backend_code()
    
    print("\n🎯 SUMMARY")
    print("==========")
    print("Based on the analysis above, we can see:")
    print("1. Which login format works (OAuth2 vs JSON)")
    print("2. What fields registration requires")
    print("3. The exact validation errors")
    print("4. Backend model specifications")
    print("\nUse this info to fix the frontend authentication!")

if __name__ == "__main__":
    main()
