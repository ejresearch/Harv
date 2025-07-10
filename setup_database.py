#!/usr/bin/env python3
"""
Complete Database Setup and Initialization Script
Place this file in your ROOT directory (same level as README.md)
Run: python setup_database.py
"""

import os
import sys
import sqlite3
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

def setup_database():
    """Complete database setup"""
    print("🚀 Starting Harv Database Setup")
    print("=" * 50)
    
    try:
        # Import after path setup
        from app.models import Base
        from app.database import engine, DATABASE_URL
        
        print("📁 Database URL:", DATABASE_URL)
        
        # Create all tables
        print("🔧 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        # Populate modules
        print("📚 Populating modules...")
        populate_modules()
        
        # Check database
        check_database()
        
        print("\n" + "=" * 50)
        print("✅ Database setup completed successfully!")
        print("\n🎯 Next steps:")
        print("1. Set your OpenAI API key: export OPENAI_API_KEY=sk-...")
        print("2. Start the backend: cd backend && uvicorn app.main:app --reload")
        print("3. Test: curl http://127.0.0.1:8000/health")
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def populate_modules():
    """Populate the 15 Mass Communication modules"""
    try:
        from app.database import SessionLocal
        from app.models import Module
        
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
        
        db = SessionLocal()
        created = 0
        
        for i, title in enumerate(mass_comm_modules, 1):
            existing = db.query(Module).filter(Module.id == i).first()
            if not existing:
                module = Module(
                    id=i,
                    title=title,
                    description=f"Module {i} of the Mass Communication course",
                    resources="",
                    system_prompt="",
                    module_prompt="",
                    system_corpus="",
                    module_corpus="",
                    dynamic_corpus="",
                    api_endpoint="https://api.openai.com/v1/chat/completions"
                )
                db.add(module)
                created += 1
                print(f"  ➕ Added Module {i}: {title}")
            else:
                print(f"  ✓ Module {i} already exists")
        
        db.commit()
        db.close()
        print(f"✅ Modules populated! Created {created} new modules")
        return True
        
    except Exception as e:
        print(f"❌ Error populating modules: {e}")
        return False

def check_database():
    """Check database structure"""
    print("🔍 Checking database structure...")
    
    try:
        from app.database import DATABASE_URL
        
        if "sqlite" in DATABASE_URL:
            db_file = DATABASE_URL.replace("sqlite:///./", "")
            if os.path.exists(db_file):
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall()]
                
                expected_tables = [
                    'users', 'modules', 'conversations', 'documents', 
                    'memory_summaries', 'user_progress', 'onboarding_surveys',
                    'course_corpus', 'module_corpus_entries'
                ]
                
                print(f"  📊 Found {len(tables)} tables:")
                for table in expected_tables:
                    if table in tables:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        print(f"    ✓ {table}: {count} records")
                    else:
                        print(f"    ❌ Missing: {table}")
                
                conn.close()
            else:
                print("  ❌ Database file not found")
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)
