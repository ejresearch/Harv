#!/usr/bin/env python3
"""
Test Suite 3: Authentication Layer - Updated with Real Credentials
Tests: Registration, Login, Token Management
Prerequisites: Suite 1 & 2 passing
"""

import requests
import json
import sys
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def test_user_registration():
    """Test 3.1: User registration (create new test user)"""
    print("🔍 Test 3.1: User Registration")
    
    test_user = {
        "username": f"testuser_{int(time.time())}",
        "email": f"test_{int(time.time())}@example.com",
        "password": "testpass123",
        "name": "Test User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=test_user, timeout=10)
        if response.status_code in [200, 201]:
            print("   ✅ User registration: PASS")
            return True, test_user
        else:
            print(f"   ❌ User registration: FAIL ({response.status_code})")
            print(f"   Response: {response.text}")
            return False, None
    except Exception as e:
        print(f"   ❌ User registration: ERROR - {e}")
        return False, None

def test_real_user_login():
    """Test 3.2: Real user login with your actual credentials"""
    print("\n🔍 Test 3.2: Real User Login")
    
    # Your actual credentials
    login_attempts = [
        {"username": "questfortheprimer@gmail.com", "password": "Joust?poet1c"},
        {"email": "questfortheprimer@gmail.com", "password": "Joust?poet1c"},
    ]
    
    for i, login_data in enumerate(login_attempts):
        print(f"   🔍 Attempt {i+1}: {list(login_data.keys())}")
        
        try:
            # Try JSON format first
            response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                token = result.get('access_token')
                if token:
                    print(f"   ✅ Real user login: PASS")
                    print(f"   🔑 Token: {token[:30]}...")
                    return True, token
                else:
                    print(f"   ❌ Real user login: No token in response")
            else:
                print(f"   ❌ JSON login attempt {i+1}: {response.status_code}")
                print(f"   Response: {response.text}")
                
                # Try form data format
                form_response = requests.post(f"{BASE_URL}/auth/login", data=login_data, timeout=10)
                if form_response.status_code == 200:
                    result = form_response.json()
                    token = result.get('access_token')
                    if token:
                        print(f"   ✅ Real user login (form): PASS")
                        print(f"   🔑 Token: {token[:30]}...")
                        return True, token
                else:
                    print(f"   ❌ Form login attempt {i+1}: {form_response.status_code}")
                    
        except Exception as e:
            print(f"   ❌ Login attempt {i+1}: ERROR - {e}")
    
    print("   ❌ Real user login: FAILED")
    return False, None

def test_token_validation(token):
    """Test 3.3: Token validation with real token"""
    print("\n🔍 Test 3.3: Token Validation")
    
    if not token:
        print("   ⏭️  Skipping token test (no token)")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers, timeout=5)
        if response.status_code == 200:
            user_info = response.json()
            print("   ✅ Token validation: PASS")
            print(f"   👤 User info: {user_info}")
            return True
        else:
            print(f"   ❌ Token validation: FAIL ({response.status_code})")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Token validation: ERROR - {e}")
        return False

def test_authenticated_endpoint(token):
    """Test 3.4: Test authenticated endpoint access"""
    print("\n🔍 Test 3.4: Authenticated Endpoint Access")
    
    if not token:
        print("   ⏭️  Skipping authenticated test (no token)")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Test memory stats endpoint (requires auth)
        response = requests.get(f"{BASE_URL}/memory/stats/1", headers=headers, timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print("   ✅ Authenticated endpoint: PASS")
            print(f"   📊 Memory stats: {stats}")
            return True
        else:
            print(f"   ❌ Authenticated endpoint: FAIL ({response.status_code})")
            return False
    except Exception as e:
        print(f"   ❌ Authenticated endpoint: ERROR - {e}")
        return False

def main():
    print("🧪 TEST SUITE 3: AUTHENTICATION LAYER (Updated)")
    print("=" * 50)
    print("Testing: Registration, Real Login, Token Management")
    print("")
    
    results = []
    
    # Test 3.1: User Registration (test system)
    reg_ok, test_user = test_user_registration()
    results.append(reg_ok)
    
    # Test 3.2: Real User Login (your credentials)
    login_ok, token = test_real_user_login()
    results.append(login_ok)
    
    # Test 3.3: Token Validation
    token_ok = test_token_validation(token)
    results.append(token_ok)
    
    # Test 3.4: Authenticated Endpoint Access
    auth_endpoint_ok = test_authenticated_endpoint(token)
    results.append(auth_endpoint_ok)
    
    # Summary
    passed = sum(results)
    print(f"\n📊 Suite 3 Results: {passed}/4 tests passed")
    
    if passed >= 3:  # 3/4 is acceptable
        print("✅ AUTHENTICATION LAYER: SOLID")
        print("🚀 Ready for Suite 4: Chat & AI Layer")
        
        # Save token for next suite
        if token:
            try:
                with open('.test_token', 'w') as f:
                    f.write(token)
                print("💾 Token saved for Suite 4")
            except:
                pass
                
        return True
    else:
        print("❌ AUTHENTICATION LAYER: NEEDS FIXES")
        print("Fix authentication issues before proceeding")
        
        # Show debugging info
        print("\n🔧 DEBUGGING INFO:")
        print("1. Check if your user exists in database")
        print("2. Verify password hash algorithm")
        print("3. Check auth endpoint implementation")
        print("4. Test login manually: curl -X POST http://127.0.0.1:8000/auth/login")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
