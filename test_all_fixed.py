#!/usr/bin/env python3
"""
Complete Test Script for Fixed Harv Backend
Place in ROOT directory and run: python test_all_fixed.py
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    """Test health endpoint"""
    print("🏥 Testing health endpoint...")
    try:
        r = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            print(f"   ✅ Health: {r.json()}")
            return True
        else:
            print(f"   ❌ Health failed: {r.text}")
            return False
    except Exception as e:
        print(f"   ❌ Health error: {e}")
        return False

def test_modules():
    """Test modules endpoint"""
    print("📚 Testing modules endpoint...")
    try:
        r = requests.get(f"{BASE_URL}/modules")
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            modules = r.json()
            print(f"   ✅ Found {len(modules)} modules")
            return len(modules) > 0
        else:
            print(f"   ❌ Modules failed: {r.text}")
            return False
    except Exception as e:
        print(f"   ❌ Modules error: {e}")
        return False

def test_populate_modules():
    """Test populating modules"""
    print("📚 Testing module population...")
    try:
        r = requests.post(f"{BASE_URL}/modules/populate")
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            result = r.json()
            print(f"   ✅ Populate result: {result}")
            return True
        else:
            print(f"   ❌ Populate failed: {r.text}")
            return False
    except Exception as e:
        print(f"   ❌ Populate error: {e}")
        return False

def test_registration():
    """Test user registration"""
    print("👤 Testing user registration...")
    try:
        test_user = {
            "email": f"test_{datetime.now().timestamp()}@harv.example.com",
            "password": "testpassword123",
            "name": "Test User",
            "reason": "Learning mass communication",
            "familiarity": "Somewhat familiar",
            "learning_style": "Visual",
            "goals": "Understand media theory",
            "background": "Student"
        }
        
        r = requests.post(f"{BASE_URL}/auth/register", json=test_user)
        print(f"   Status: {r.status_code}")
        
        if r.status_code == 200:
            result = r.json()
            print(f"   ✅ Registration successful: User ID {result.get('user_id')}")
            print(f"   🔑 Access token: {result.get('access_token', 'N/A')[:20]}...")
            return result
        else:
            print(f"   ❌ Registration failed: {r.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Registration error: {e}")
        return None

def test_login(email, password):
    """Test user login"""
    print("🔑 Testing user login...")
    try:
        login_data = {
            "email": email,
            "password": password
        }
        
        r = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"   Status: {r.status_code}")
        
        if r.status_code == 200:
            result = r.json()
            print(f"   ✅ Login successful: User ID {result.get('user_id')}")
            return result
        else:
            print(f"   ❌ Login failed: {r.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return None

def test_profile(access_token):
    """Test user profile endpoint"""
    print("👤 Testing user profile...")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        r = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        print(f"   Status: {r.status_code}")
        
        if r.status_code == 200:
            profile = r.json()
            print(f"   ✅ Profile: {profile['user']['name']} ({profile['user']['email']})")
            if profile.get('onboarding'):
                print(f"   ✅ Onboarding data found")
            return True
        else:
            print(f"   ❌ Profile failed: {r.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Profile error: {e}")
        return False

def test_chat(user_id, module_id=1):
    """Test chat endpoint"""
    print("💬 Testing chat endpoint...")
    try:
        chat_data = {
            "user_id": user_id,
            "module_id": module_id,
            "message": "What is mass communication?"
        }
        
        r = requests.post(f"{BASE_URL}/chat/", json=chat_data)
        print(f"   Status: {r.status_code}")
        
        if r.status_code == 200:
            result = r.json()
            print(f"   ✅ Chat response: {result.get('reply', 'N/A')[:100]}...")
            print(f"   📝 Conversation ID: {result.get('conversation_id')}")
            return result
        else:
            print(f"   ❌ Chat failed: {r.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Chat error: {e}")
        return None

def test_memory(user_id, module_id=1):
    """Test memory endpoints"""
    print("🧠 Testing memory endpoints...")
    try:
        # Save memory summary
        memory_data = {
            "user_id": user_id,
            "module_id": module_id,
            "what_learned": "Mass communication is the process of transmitting messages to large audiences",
            "how_learned": "Through Socratic questioning with AI tutor"
        }
        
        r = requests.post(f"{BASE_URL}/memory/summary", json=memory_data)
        print(f"   Memory save status: {r.status_code}")
        
        if r.status_code == 200:
            print(f"   ✅ Memory saved: {r.json()}")
        else:
            print(f"   ❌ Memory save failed: {r.text}")
            return False
        
        # Get conversation history
        history_data = {
            "user_id": user_id,
            "module_id": module_id
        }
        
        r = requests.post(f"{BASE_URL}/conversation/history", json=history_data)
        print(f"   History status: {r.status_code}")
        
        if r.status_code == 200:
            history = r.json()
            print(f"   ✅ Found {len(history.get('history', []))} messages in history")
            return True
        else:
            print(f"   ❌ History failed: {r.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Memory error: {e}")
        return False

def main():
    """Run complete test suite"""
    print("🚀 HARV BACKEND COMPLETE TEST SUITE")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Health
    results['health'] = test_health()
    
    # Test 2: Modules
    results['populate'] = test_populate_modules()
    results['modules'] = test_modules()
    
    # Test 3: Registration
    reg_result = test_registration()
    results['registration'] = reg_result is not None
    
    if not reg_result:
        print("\n❌ Cannot continue tests without successful registration")
        return
    
    user_email = reg_result.get('user', {}).get('email') or f"test_{datetime.now().timestamp()}@harv.example.com"
    user_id = reg_result.get('user_id')
    access_token = reg_result.get('access_token')
    
    # Test 4: Login
    login_result = test_login(user_email, "testpassword123")
    results['login'] = login_result is not None
    
    # Test 5: Profile
    if access_token:
        results['profile'] = test_profile(access_token)
    
    # Test 6: Chat
    if user_id:
        chat_result = test_chat(user_id)
        results['chat'] = chat_result is not None
        
        # Test 7: Memory
        results['memory'] = test_memory(user_id)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name.upper():15} {status}")
    
    print(f"\n🎯 OVERALL: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Your backend is working perfectly!")
        print("\n🚀 Ready for frontend integration!")
    elif passed_tests >= total_tests * 0.8:
        print("⚠️  Most tests passed - minor issues remain")
    else:
        print("❌ Major issues detected - check error messages above")
    
    print("\n🔗 Test your API manually:")
    print("   Health:  curl http://127.0.0.1:8000/health")
    print("   Modules: curl http://127.0.0.1:8000/modules")
    print("   GUI:     http://localhost:3000/dev-gui.html")

if __name__ == "__main__":
    main()
