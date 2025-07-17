#!/usr/bin/env python3
"""
Final Database Verification Test
Run from backend directory: python test_final_verification.py
"""

import sys
import os
import sqlite3

# Add parent directory to path to import backend modules
sys.path.append('.')

def test_database_direct():
    """Test database directly with SQLite"""
    print("🗄️ DIRECT DATABASE TEST")
    print("=" * 40)
    
    # Test both possible database locations
    db_locations = [
        "../harv.db",  # Root database (should be primary)
        "./harv.db",   # Backend database (if exists)
        "harv.db"      # Current directory
    ]
    
    for db_path in db_locations:
        print(f"\n📄 Testing: {db_path}")
        
        if not os.path.exists(db_path):
            print(f"   ❌ Not found")
            continue
            
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Test basic tables
            cursor.execute("SELECT COUNT(*) FROM modules")
            module_count = cursor.fetchone()[0]
            print(f"   📚 Modules: {module_count}")
            
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            print(f"   👥 Users: {user_count}")
            
            # Test schema completeness
            cursor.execute("PRAGMA table_info(documents)")
            doc_cols = [row[1] for row in cursor.fetchall()]
            has_user_id = 'user_id' in doc_cols
            print(f"   📄 Documents user_id: {'✅' if has_user_id else '❌'}")
            
            cursor.execute("PRAGMA table_info(memory_summaries)")
            memory_cols = [row[1] for row in cursor.fetchall()]
            has_conversation_id = 'conversation_id' in memory_cols
            has_key_concepts = 'key_concepts' in memory_cols
            print(f"   🧠 Memory conversation_id: {'✅' if has_conversation_id else '❌'}")
            print(f"   🧠 Memory key_concepts: {'✅' if has_key_concepts else '❌'}")
            
            # Test module configuration
            cursor.execute("SELECT COUNT(*) FROM modules WHERE api_endpoint IS NOT NULL")
            configured_modules = cursor.fetchone()[0]
            print(f"   ⚙️  Configured modules: {configured_modules}/15")
            
            conn.close()
            
            # If this database looks good, recommend it
            if module_count == 15 and has_user_id and has_conversation_id:
                print(f"   ✅ RECOMMENDED DATABASE: {db_path}")
                return db_path
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return None

def test_backend_models():
    """Test backend models with current database configuration"""
    print("\n🔗 BACKEND MODELS TEST")
    print("=" * 40)
    
    try:
        from app.database import SessionLocal, DATABASE_URL
        from app.models import Module, User, Conversation, MemorySummary, Document
        
        print(f"📍 Database URL: {DATABASE_URL}")
        
        # Test database connection
        db = SessionLocal()
        
        # Test each model
        models_to_test = [
            ("Module", Module),
            ("User", User), 
            ("Conversation", Conversation),
            ("MemorySummary", MemorySummary),
            ("Document", Document)
        ]
        
        results = {}
        
        for model_name, model_class in models_to_test:
            try:
                count = db.query(model_class).count()
                print(f"   ✅ {model_name}: {count} records")
                results[model_name] = True
            except Exception as e:
                print(f"   ❌ {model_name}: {e}")
                results[model_name] = False
        
        # Test user creation without cascade issues
        try:
            from app.auth import get_password_hash
            
            # Try to create a simple user without triggering cascade relationships
            hashed_password = get_password_hash("testpass123")
            
            # Check if test user exists first
            existing = db.query(User).filter(User.email == "simple_test@harv.test").first()
            if existing:
                print(f"   ✅ Test user already exists: ID={existing.id}")
            else:
                # Create user without any relationships
                test_user = User(
                    email="simple_test@harv.test",
                    hashed_password=hashed_password,
                    name="Simple Test User"
                )
                
                db.add(test_user)
                db.commit()
                db.refresh(test_user)
                
                print(f"   ✅ Created test user: ID={test_user.id}")
                
                # Clean up
                db.delete(test_user)
                db.commit()
                print(f"   ✅ Cleaned up test user")
            
            results["UserCreation"] = True
            
        except Exception as e:
            print(f"   ❌ User creation test: {e}")
            results["UserCreation"] = False
        
        db.close()
        
        # Summary
        passed_tests = sum(1 for result in results.values() if result)
        total_tests = len(results)
        
        print(f"\n📊 Backend Models: {passed_tests}/{total_tests} tests passed")
        return passed_tests == total_tests
        
    except Exception as e:
        print(f"❌ Backend models test failed: {e}")
        return False

def test_configuration_completeness():
    """Test that all required configurations are in place"""
    print("\n⚙️ CONFIGURATION COMPLETENESS TEST")
    print("=" * 40)
    
    try:
        from app.database import SessionLocal
        from app.models import Module
        
        db = SessionLocal()
        
        # Check module configuration completeness
        modules = db.query(Module).all()
        
        if len(modules) != 15:
            print(f"   ❌ Expected 15 modules, found {len(modules)}")
            return False
        
        configured_count = 0
        for module in modules:
            has_api_endpoint = bool(getattr(module, 'api_endpoint', None))
            has_system_prompt = bool(getattr(module, 'system_prompt', None))
            has_memory_config = bool(getattr(module, 'memory_extraction_prompt', None))
            
            if has_api_endpoint and has_system_prompt:
                configured_count += 1
        
        print(f"   📚 Modules with basic config: {configured_count}/15")
        
        # Check for memory system fields
        sample_module = modules[0]
        memory_fields = [
            'memory_extraction_prompt', 'mastery_triggers', 'confusion_triggers',
            'memory_context_template', 'cross_module_references', 'memory_weight'
        ]
        
        memory_field_count = sum(1 for field in memory_fields if hasattr(sample_module, field))
        print(f"   🧠 Memory system fields: {memory_field_count}/{len(memory_fields)}")
        
        db.close()
        
        success = (configured_count == 15 and memory_field_count >= 4)
        print(f"   {'✅' if success else '❌'} Configuration completeness")
        
        return success
        
    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
        return False

def main():
    """Run all verification tests"""
    print("🧪 FINAL DATABASE VERIFICATION")
    print("=" * 60)
    
    # Test 1: Direct database access
    recommended_db = test_database_direct()
    
    # Test 2: Backend models
    backend_success = test_backend_models()
    
    # Test 3: Configuration completeness
    config_success = test_configuration_completeness()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 FINAL VERIFICATION SUMMARY")
    print("=" * 60)
    
    print(f"   Database accessibility: {'✅' if recommended_db else '❌'}")
    print(f"   Backend model compatibility: {'✅' if backend_success else '❌'}")
    print(f"   Configuration completeness: {'✅' if config_success else '❌'}")
    
    if recommended_db:
        print(f"\n📍 Using database: {recommended_db}")
    
    all_passed = bool(recommended_db) and backend_success and config_success
    
    if all_passed:
        print("\n🎉 ALL VERIFICATION TESTS PASSED!")
        print("\n🎯 Ready for next steps:")
        print("   1. ✅ Database fully resolved")
        print("   2. 🚀 Start backend: uvicorn app.main:app --reload") 
        print("   3. 🧪 Test endpoints: curl http://127.0.0.1:8000/health")
        print("   4. 🔄 Continue with Environment Configuration")
    else:
        print("\n❌ Some verification tests failed")
        print("🔧 Run fix_database_location.py to resolve remaining issues")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
