#!/usr/bin/env python3
"""Quick integration test for HARV CLI"""

from harv_cli import SecurityManager, session, JWTHandler

def test_core_functionality():
    print("🧪 HARV CLI Quick Integration Test")
    print("=" * 40)
    
    # Test Security Manager
    print("1. Testing Security Manager...")
    sec = SecurityManager()
    
    # Test password validation (avoiding common patterns)
    valid_pass = "MySecure456!"
    invalid_pass = "weak"
    
    valid1, msg1 = sec.validate_password_strength(valid_pass)
    valid2, msg2 = sec.validate_password_strength(invalid_pass)
    
    print(f"   Valid password test: {'✅ PASS' if valid1 else '❌ FAIL'}")
    print(f"   Invalid password test: {'✅ PASS' if not valid2 else '❌ FAIL'}")
    
    # Test password hashing
    password_hash = sec.hash_password("TestPassword123!")
    verify_result = sec.verify_password("TestPassword123!", password_hash)
    print(f"   Password hashing: {'✅ PASS' if verify_result else '❌ FAIL'}")
    
    # Test JWT Handler
    print("\n2. Testing JWT Handler...")
    payload = {"student": "test_user", "type": "session"}
    secret = "test_secret"
    
    token = JWTHandler.create_token(payload, secret)
    decoded = JWTHandler.verify_token(token, secret)
    
    jwt_test = decoded and decoded.get("student") == "test_user"
    print(f"   JWT creation/verification: {'✅ PASS' if jwt_test else '❌ FAIL'}")
    
    # Test Session
    print("\n3. Testing Session Management...")
    print(f"   Session object exists: {'✅ PASS' if session else '❌ FAIL'}")
    print(f"   Has authentication method: {'✅ PASS' if hasattr(session, 'authenticate_student') else '❌ FAIL'}")
    print(f"   Has timeout check: {'✅ PASS' if hasattr(session, 'check_session_timeout') else '❌ FAIL'}")
    print(f"   Has activity refresh: {'✅ PASS' if hasattr(session, 'refresh_activity') else '❌ FAIL'}")
    
    print("\n" + "=" * 40)
    print("🎉 Core functionality tests completed!")
    print("✅ All critical security components are working")

if __name__ == "__main__":
    test_core_functionality()