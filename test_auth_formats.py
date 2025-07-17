
#!/usr/bin/env python3
"""
Test Authentication Endpoints
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_login_formats():
    """Test different login formats"""
    
    credentials = {
        "email": "questfortheprimer@gmail.com",
        "password": "Joust?poet1c"
    }
    
    print("🧪 Testing Login Formats")
    print("========================")
    
    # Test 1: JSON format
    print("\n1. Testing JSON format...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=credentials,
            headers={"Content-Type": "application/json"}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text}")
        else:
            print("   ✅ JSON login successful")
    except Exception as e:
        print(f"   ❌ JSON login error: {e}")
    
    # Test 2: Form data format
    print("\n2. Testing form data...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data=credentials,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text}")
        else:
            print("   ✅ Form login successful")
    except Exception as e:
        print(f"   ❌ Form login error: {e}")
    
    # Test 3: OAuth2 format with username
    print("\n3. Testing OAuth2 format...")
    try:
        oauth_data = {
            "username": credentials["email"],
            "password": credentials["password"],
            "grant_type": "password"
        }
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data=oauth_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text}")
        else:
            print("   ✅ OAuth2 login successful")
    except Exception as e:
        print(f"   ❌ OAuth2 login error: {e}")

if __name__ == "__main__":
    test_login_formats()
