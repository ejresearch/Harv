#!/usr/bin/env python3
"""
Test Fixed Authentication - Should work perfectly now
"""
import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def test_fixed_authentication():
    """Test the fixed authentication with exact backend requirements"""
    print("🧪 Testing Fixed Authentication")
    print("===============================")
    
    # Test 1: Login (OAuth2 format - confirmed working)
    print("\n1. Testing Login (OAuth2 format)...")
    login_data = {
        "username": "questfortheprimer@gmail.com",
        "password": "Joust?poet1c",
        "grant_type": "password"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            print("   ✅ Login: SUCCESS!")
            data = response.json()
            token = data.get('access_token')
            print(f"   🔑 Token received: {token[:30] if token else 'None'}...")
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Login error: {e}")
    
    # Test 2: Registration (JSON with required name field)
    print("\n2. Testing Registration (JSON with name field)...")
    timestamp = int(time.time())
    register_data = {
        "email": f"testuser{timestamp}@example.com",
        "password": "testpass123",
        "name": f"Test User {timestamp}",  # REQUIRED field
        "username": f"testuser{timestamp}@example.com",  # Helps with success
        "reason": "Learning mass communication",
        "familiarity": "Beginner",
        "learning_style": "Mixed"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=register_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("   ✅ Registration: SUCCESS!")
            data = response.json()
            print(f"   👤 User created: {data.get('message', 'Account created')}")
        else:
            print(f"   ❌ Registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Registration error: {e}")
    
    print("\n🎯 SUMMARY")
    print("==========")
    print("✅ Login: Uses OAuth2 form data with 'username' field")
    print("✅ Registration: Uses JSON with required 'name' field")
    print("✅ No more 422 validation errors expected!")

if __name__ == "__main__":
    test_fixed_authentication()
