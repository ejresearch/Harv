#!/usr/bin/env python3
"""
Quick test to verify models work with your database
"""

def test_models():
    print("🧪 Testing compatible models...")
    
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))
        
        from app.database import SessionLocal
        from app.models import Module, User, Conversation
        
        db = SessionLocal()
        
        # Test modules
        modules = db.query(Module).all()
        print(f"✅ Modules: {len(modules)} found")
        
        # Test users  
        users = db.query(User).all()
        print(f"✅ Users: {len(users)} found")
        
        # Test conversations
        conversations = db.query(Conversation).all()
        print(f"✅ Conversations: {len(conversations)} found")
        
        # Show first module details
        if modules:
            m = modules[0]
            print(f"\n📄 Sample Module:")
            print(f"   ID: {m.id}")
            print(f"   Title: {m.title}")
            print(f"   Has module_prompt: {hasattr(m, 'module_prompt')}")
            print(f"   Has api_endpoint: {hasattr(m, 'api_endpoint')}")
        
        db.close()
        print("\n🎉 All model tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

def test_backend_import():
    print("\n🔗 Testing backend imports...")
    
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))
        
        from app.auth_working import get_password_hash, authenticate_user
        from app.main import app
        
        print("✅ Auth system imports OK")
        print("✅ Main app imports OK")
        print("✅ Backend should start successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Backend import failed: {e}")
        return False

if __name__ == "__main__":
    if test_models() and test_backend_import():
        print("\n🚀 READY TO START BACKEND!")
        print("   cd backend")
        print("   uvicorn app.main:app --reload")
    else:
        print("\n❌ Issues remain - check errors above")
