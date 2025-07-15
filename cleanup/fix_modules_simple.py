#!/usr/bin/env python3
"""
Simple Fix for Module Population Issue
Just populates modules without timestamp columns
"""

import sqlite3
import os
from datetime import datetime

def fix_modules():
    """Simple fix to populate modules"""
    print("🔧 SIMPLE MODULE FIX")
    print("=" * 30)
    
    db_file = "harv.db"
    if not os.path.exists(db_file):
        print("❌ Database file not found")
        return False
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    try:
        # Check current modules table structure
        cursor.execute("PRAGMA table_info(modules)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 Available columns: {columns}")
        
        # Simple module data (only using existing columns)
        mass_comm_modules = [
            "Introduction to Mass Communication",
            "History and Evolution of Media", 
            "Media Theory and Effects",
            "Print Media and Journalism",
            "Broadcasting: Radio and Television",
            "Digital Media and the Internet",
            "Social Media and New Platforms",
            "Media Ethics and Responsibility",
            "Media Law and Regulation",
            "Advertising and Public Relations",
            "Media Economics and Business Models",
            "Global Media and Cultural Impact",
            "Media Literacy and Critical Analysis",
            "Future of Mass Communication",
            "Capstone: Integrating Knowledge"
        ]
        
        print("📚 Populating modules with available columns...")
        
        for i, title in enumerate(mass_comm_modules, 1):
            # Check if module exists
            cursor.execute("SELECT id FROM modules WHERE id = ?", (i,))
            if not cursor.fetchone():
                # Build INSERT based on available columns
                if 'api_endpoint' in columns:
                    cursor.execute("""
                        INSERT INTO modules (id, title, description, resources, api_endpoint)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        i, 
                        title, 
                        f"Module {i} of the Mass Communication course",
                        "",
                        "https://api.openai.com/v1/chat/completions"
                    ))
                else:
                    cursor.execute("""
                        INSERT INTO modules (id, title, description, resources)
                        VALUES (?, ?, ?, ?)
                    """, (
                        i, 
                        title, 
                        f"Module {i} of the Mass Communication course",
                        ""
                    ))
                print(f"   ➕ Added Module {i}: {title}")
            else:
                print(f"   ✓ Module {i} already exists")
        
        conn.commit()
        print("✅ Modules populated successfully!")
        
        # Verify
        cursor.execute("SELECT COUNT(*) FROM modules")
        count = cursor.fetchone()[0]
        print(f"📊 Total modules in database: {count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        conn.close()
        return False

def test_backend_connection():
    """Test if backend will work now"""
    print("\n🔗 Testing backend compatibility...")
    
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))
        
        from app.database import SessionLocal
        from app.models import Module
        
        db = SessionLocal()
        modules = db.query(Module).all()
        print(f"✅ SQLAlchemy can query modules: {len(modules)} found")
        
        for module in modules[:3]:  # Show first 3
            print(f"   📄 Module {module.id}: {module.title}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Running simple module fix...")
    
    if fix_modules():
        if test_backend_connection():
            print("\n🎉 SUCCESS! Your backend should work now!")
            print("\n🎯 Next steps:")
            print("   cd backend")
            print("   uvicorn app.main:app --reload")
        else:
            print("\n⚠️  Modules fixed but backend compatibility issue remains")
    else:
        print("\n❌ Fix failed")
