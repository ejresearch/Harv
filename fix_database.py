#!/usr/bin/env python3
"""
One-Click Database Fix Script
Run: python fix_database.py
"""

import sqlite3
import os
import sys
from datetime import datetime

def fix_database():
    """Fix all database schema issues with one script"""
    print("🔧 FIXING DATABASE SCHEMA ISSUES")
    print("=" * 50)
    
    db_file = "harv.db"
    if not os.path.exists(db_file):
        print("❌ Database file not found. Please run the backend first to create it.")
        return False
    
    # Backup database
    backup_file = f"harv_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    os.system(f"cp {db_file} {backup_file}")
    print(f"📁 Created backup: {backup_file}")
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    try:
        # Fix 1: Ensure consistent password field in users table
        print("1. Fixing users table schema...")
        cursor.execute("PRAGMA table_info(users)")
        user_columns = [row[1] for row in cursor.fetchall()]
        
        if 'password' in user_columns and 'hashed_password' not in user_columns:
            cursor.execute("ALTER TABLE users RENAME COLUMN password TO hashed_password")
            print("   ✅ Renamed 'password' to 'hashed_password'")
        elif 'hashed_password' not in user_columns:
            print("   ⚠️  No password column found - this might be fine")
        else:
            print("   ✅ Password field already correct")
        
        # Fix 2: Ensure modules table has all GUI fields
        print("2. Fixing modules table schema...")
        cursor.execute("PRAGMA table_info(modules)")
        module_columns = [row[1] for row in cursor.fetchall()]
        
        missing_fields = [
            ("module_prompt", "TEXT"),
            ("system_corpus", "TEXT"),
            ("module_corpus", "TEXT"),
            ("dynamic_corpus", "TEXT"),
            ("api_endpoint", "TEXT")
        ]
        
        for field_name, field_type in missing_fields:
            if field_name not in module_columns:
                cursor.execute(f"ALTER TABLE modules ADD COLUMN {field_name} {field_type}")
                print(f"   ✅ Added {field_name} column")
            else:
                print(f"   ✅ {field_name} already exists")
        
        # Fix 3: Add missing conversation fields
        print("3. Fixing conversations table schema...")
        cursor.execute("PRAGMA table_info(conversations)")
        conv_columns = [row[1] for row in cursor.fetchall()]
        
        conv_missing_fields = [
            ("title", "TEXT"),
            ("current_grade", "TEXT"),
            ("memory_summary", "TEXT"),
            ("finalized", "BOOLEAN DEFAULT FALSE"),
            ("updated_at", "DATETIME")
        ]
        
        for field_name, field_type in conv_missing_fields:
            if field_name not in conv_columns:
                cursor.execute(f"ALTER TABLE conversations ADD COLUMN {field_name} {field_type}")
                print(f"   ✅ Added {field_name} column")
            else:
                print(f"   ✅ {field_name} already exists")
        
        # Fix 4: Set default values for API endpoint
        print("4. Setting default API endpoints...")
        cursor.execute("""
            UPDATE modules 
            SET api_endpoint = 'https://api.openai.com/v1/chat/completions' 
            WHERE api_endpoint IS NULL OR api_endpoint = ''
        """)
        
        # Fix 5: Ensure we have all 15 modules
        print("5. Ensuring all 15 modules exist...")
        modules = [
            "Introduction to Mass Communication", "History and Evolution of Media", 
            "Media Theory and Effects", "Print Media and Journalism",
            "Broadcasting: Radio and Television", "Digital Media and the Internet",
            "Social Media and New Platforms", "Media Ethics and Responsibility",
            "Media Law and Regulation", "Advertising and Public Relations",
            "Media Economics and Business Models", "Global Media and Cultural Impact",
            "Media Literacy and Critical Analysis", "Future of Mass Communication",
            "Capstone: Integrating Knowledge"
        ]
        
        for i, title in enumerate(modules, 1):
            cursor.execute("SELECT id FROM modules WHERE id = ?", (i,))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO modules (id, title, description, resources, api_endpoint)
                    VALUES (?, ?, ?, ?, ?)
                """, (i, title, f"Module {i} of the Mass Communication course", "", 
                     "https://api.openai.com/v1/chat/completions"))
                print(f"   ➕ Added Module {i}: {title}")
        
        conn.commit()
        print("\n✅ All database fixes completed successfully!")
        
        # Verification
        print("\n🔍 Verification:")
        cursor.execute("SELECT COUNT(*) FROM modules")
        module_count = cursor.fetchone()[0]
        print(f"   📚 Modules in database: {module_count}")
        
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"   👥 Users in database: {user_count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database fix failed: {e}")
        conn.rollback()
        conn.close()
        return False

def test_backend_connection():
    """Test if backend will work with fixed database"""
    print("\n🔗 Testing backend compatibility...")
    
    try:
        # Add backend to path
        sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))
        
        from app.database import SessionLocal
        from app.models import Module, User
        
        db = SessionLocal()
        
        # Test module query
        modules = db.query(Module).all()
        print(f"✅ Can query modules: {len(modules)} found")
        
        # Test user query  
        users = db.query(User).all()
        print(f"✅ Can query users: {len(users)} found")
        
        # Test module has GUI fields
        if modules:
            m = modules[0]
            has_system_prompt = hasattr(m, 'system_prompt')
            has_module_prompt = hasattr(m, 'module_prompt')
            print(f"✅ GUI fields available: system_prompt={has_system_prompt}, module_prompt={has_module_prompt}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Backend compatibility test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting One-Click Database Fix...")
    
    if fix_database():
        if test_backend_connection():
            print("\n🎉 SUCCESS! Database is fixed and backend ready!")
            print("\n🎯 Next steps:")
            print("1. Start backend: cd backend && uvicorn app.main:app --reload")
            print("2. Test GUI: http://localhost:3000/dev-gui.html")
            print("3. Start frontend: cd frontend && npm run dev")
        else:
            print("\n⚠️  Database fixed but backend test failed")
    else:
        print("\n❌ Database fix failed")
