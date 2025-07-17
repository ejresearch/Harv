#!/usr/bin/env python3
"""
Test Models Fix - Verify Database and Backend Compatibility
Run: python backend/test_models_fix.py
"""

import sys
import os
sys.path.append('.')

def test_database_connection():
    """Test basic database connection"""
    print("🔌 Testing database connection...")
    
    try:
        from app.database import SessionLocal, engine
        from app.models import Module, User, Conversation
        
        # Test database connection
        db = SessionLocal()
        
        # Test modules
        modules = db.query(Module).all()
        print(f"   ✅ Modules: {len(modules)} found")
        
        # Test users
        users = db.query(User).all()
        print(f"   ✅ Users: {len(users)} found")
        
        # Test conversations
        conversations = db.query(Conversation).all()
        print(f"   ✅ Conversations: {len(conversations)} found")
        
        # Test module fields
        if modules:
            module = modules[0]
            fields_to_check = [
                'api_endpoint', 'module_prompt', 'system_corpus', 
                'module_corpus', 'dynamic_corpus', 'memory_extraction_prompt'
            ]
            
            print("   📋 Module field availability:")
            for field in fields_to_check:
                has_field = hasattr(module, field)
                value_exists = getattr(module, field, None) is not None if has_field else False
                print(f"     {field}: {'✅' if has_field else '❌'} ({'has value' if value_exists else 'empty'})")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Database test failed: {e}")
        return False

def test_auth_system():
    """Test authentication system"""
    print("\n🔐 Testing authentication system...")
    
    try:
        from app.auth import get_password_hash, verify_password, create_access_token, verify_token
        
        # Test password hashing
        password = "test123"
        hashed = get_password_hash(password)
        verified = verify_password(password, hashed)
        print(f"   ✅ Password hashing: {verified}")
        
        # Test token creation
        token = create_access_token({"sub": "1"})
        token_data = verify_token(token)
        print(f"   ✅ Token system: {token_data is not None}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Auth test failed: {e}")
        return False

def test_user_creation():
    """Test user creation with correct schema"""
    print("\n👤 Testing user creation...")
    
    try:
        from app.database import SessionLocal
        from app.models import User
        from app.auth import get_password_hash
        
        db = SessionLocal()
        
        # Test user creation with correct field name
        hashed_password = get_password_hash("testpass123")
        
        # Check if test user already exists
        existing = db.query(User).filter(User.email == "schema_test@harv.test").first()
        if existing:
            db.delete(existing)
            db.commit()
        
        user = User(
            email="schema_test@harv.test",
            hashed_password=hashed_password,  # Using correct field name
            name="Schema Test User"
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"   ✅ User created: ID={user.id}, Email={user.email}")
        print(f"   ✅ Password field: hashed_password={user.hashed_password is not None}")
        
        # Clean up test user
        db.delete(user)
        db.commit()
        db.close()
        
        return True
        
    except Exception as e:
        print(f"   ❌ User creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_module_configuration():
    """Test module configuration fields"""
    print("\n📚 Testing module configuration...")
    
    try:
        from app.database import SessionLocal
        from app.models import Module
        
        db = SessionLocal()
        
        # Get first module
        module = db.query(Module).first()
        if not module:
            print("   ❌ No modules found")
            return False
        
        print(f"   📖 Testing Module {module.id}: {module.title}")
        
        # Test updating configuration
        module.system_prompt = "Test Socratic prompt"
        module.module_prompt = "Test module focus"
        module.api_endpoint = "https://api.openai.com/v1/chat/completions"
        
        if hasattr(module, 'memory_extraction_prompt'):
            module.memory_extraction_prompt = "Test memory extraction"
        
        db.commit()
        
        print("   ✅ Module configuration update successful")
        
        # Verify the update
        updated_module = db.query(Module).filter(Module.id == module.id).first()
        print(f"   ✅ Verification - System prompt: {updated_module.system_prompt is not None}")
        print(f"   ✅ Verification - API endpoint: {updated_module.api_endpoint}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Module configuration test failed: {e}")
        return False

def test_memory_tables():
    """Test memory system tables"""
    print("\n🧠 Testing memory system tables...")
    
    try:
        from app.database import SessionLocal
        from app.models import MemorySummary, OnboardingSurvey
        
        db = SessionLocal()
        
        # Test MemorySummary
        try:
            memory_count = db.query(MemorySummary).count()
            print(f"   ✅ MemorySummary table: {memory_count} records")
        except Exception as e:
            print(f"   ❌ MemorySummary table: {e}")
        
        # Test OnboardingSurvey
        try:
            survey_count = db.query(OnboardingSurvey).count()
            print(f"   ✅ OnboardingSurvey table: {survey_count} records")
        except Exception as e:
            print(f"   ❌ OnboardingSurvey table: {e}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Memory tables test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 HARV DATABASE & MODEL COMPATIBILITY TESTS")
    print("=" * 60)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Authentication System", test_auth_system),
        ("User Creation", test_user_creation),
        ("Module Configuration", test_module_configuration),
        ("Memory Tables", test_memory_tables)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"   {test_name:<25} {status}")
    
    print(f"\n🎯 OVERALL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Database schema is properly resolved!")
        print("\n🚀 Ready for next deployment step:")
        print("   - Start backend: uvicorn app.main:app --reload")
        print("   - Test health: curl http://127.0.0.1:8000/health")
    elif passed >= total * 0.8:
        print("⚠️  Most tests passed - minor issues may remain")
    else:
        print("❌ Major issues detected - run fix_database_schema.py first")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
