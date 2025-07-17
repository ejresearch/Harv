#!/usr/bin/env python3
"""
Database Migration Script - Updates Existing Database Schema
Run this to fix the "no such column: modules.module_prompt" error
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Migrate existing database to new schema"""
    print("🔧 MIGRATING EXISTING DATABASE SCHEMA")
    print("=" * 50)
    
    db_file = "harv.db"
    if not os.path.exists(db_file):
        print("❌ Database file not found")
        return False
    
    # Backup database first
    backup_file = f"harv_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    os.system(f"cp {db_file} {backup_file}")
    print(f"📁 Created backup: {backup_file}")
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    try:
        print("🔍 Checking current schema...")
        
        # Check modules table structure
        cursor.execute("PRAGMA table_info(modules)")
        modules_columns = [row[1] for row in cursor.fetchall()]
        print(f"   Current modules columns: {modules_columns}")
        
        # Add missing columns to modules table
        missing_module_columns = [
            ("module_prompt", "TEXT"),
            ("system_corpus", "TEXT"), 
            ("module_corpus", "TEXT"),
            ("dynamic_corpus", "TEXT"),
            ("api_endpoint", "TEXT DEFAULT 'https://api.openai.com/v1/chat/completions'"),
            ("learning_objectives", "TEXT"),
            ("created_at", "DATETIME DEFAULT CURRENT_TIMESTAMP"),
            ("updated_at", "DATETIME DEFAULT CURRENT_TIMESTAMP")
        ]
        
        print("➕ Adding missing columns to modules table...")
        for column_name, column_type in missing_module_columns:
            if column_name not in modules_columns:
                try:
                    cursor.execute(f"ALTER TABLE modules ADD COLUMN {column_name} {column_type}")
                    print(f"   ✅ Added {column_name}")
                except sqlite3.OperationalError as e:
                    print(f"   ⚠️  {column_name}: {e}")
        
        # Check users table
        cursor.execute("PRAGMA table_info(users)")
        users_columns = [row[1] for row in cursor.fetchall()]
        print(f"   Current users columns: {users_columns}")
        
        # Add missing columns to users table
        missing_user_columns = [
            ("created_at", "DATETIME DEFAULT CURRENT_TIMESTAMP"),
            ("updated_at", "DATETIME DEFAULT CURRENT_TIMESTAMP")
        ]
        
        for column_name, column_type in missing_user_columns:
            if column_name not in users_columns:
                try:
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}")
                    print(f"   ✅ Added users.{column_name}")
                except sqlite3.OperationalError as e:
                    print(f"   ⚠️  users.{column_name}: {e}")
        
        # Check conversations table
        cursor.execute("PRAGMA table_info(conversations)")
        conv_columns = [row[1] for row in cursor.fetchall()]
        print(f"   Current conversations columns: {conv_columns}")
        
        # Add missing columns to conversations table
        missing_conv_columns = [
            ("title", "TEXT DEFAULT 'New Conversation'"),
            ("current_grade", "TEXT"),
            ("memory_summary", "TEXT"),
            ("finalized", "BOOLEAN DEFAULT FALSE"),
            ("created_at", "DATETIME DEFAULT CURRENT_TIMESTAMP"),
            ("updated_at", "DATETIME DEFAULT CURRENT_TIMESTAMP")
        ]
        
        for column_name, column_type in missing_conv_columns:
            if column_name not in conv_columns:
                try:
                    cursor.execute(f"ALTER TABLE conversations ADD COLUMN {column_name} {column_type}")
                    print(f"   ✅ Added conversations.{column_name}")
                except sqlite3.OperationalError as e:
                    print(f"   ⚠️  conversations.{column_name}: {e}")
        
        # Add missing columns to user_progress table
        cursor.execute("PRAGMA table_info(user_progress)")
        progress_columns = [row[1] for row in cursor.fetchall()]
        
        missing_progress_columns = [
            ("time_spent", "INTEGER DEFAULT 0"),
            ("attempts", "INTEGER DEFAULT 0")
        ]
        
        for column_name, column_type in missing_progress_columns:
            if column_name not in progress_columns:
                try:
                    cursor.execute(f"ALTER TABLE user_progress ADD COLUMN {column_name} {column_type}")
                    print(f"   ✅ Added user_progress.{column_name}")
                except sqlite3.OperationalError as e:
                    print(f"   ⚠️  user_progress.{column_name}: {e}")
        
        # Add documents.user_id if missing
        cursor.execute("PRAGMA table_info(documents)")
        doc_columns = [row[1] for row in cursor.fetchall()]
        
        if "user_id" not in doc_columns:
            try:
                cursor.execute("ALTER TABLE documents ADD COLUMN user_id INTEGER")
                print("   ✅ Added documents.user_id")
            except sqlite3.OperationalError as e:
                print(f"   ⚠️  documents.user_id: {e}")
        
        conn.commit()
        print("✅ Database migration completed!")
        
        # Now try to populate modules again
        print("\n📚 Attempting to populate modules...")
        populate_modules_direct(cursor)
        conn.commit()
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        conn.close()
        return False

def populate_modules_direct(cursor):
    """Populate modules using direct SQL"""
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
    
    for i, title in enumerate(mass_comm_modules, 1):
        # Check if module exists
        cursor.execute("SELECT id FROM modules WHERE id = ?", (i,))
        if not cursor.fetchone():
            # Insert new module
            cursor.execute("""
                INSERT INTO modules (id, title, description, resources, api_endpoint, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                i, 
                title, 
                f"Module {i} of the Mass Communication course",
                "",
                "https://api.openai.com/v1/chat/completions",
                datetime.now().isoformat()
            ))
            print(f"   ➕ Added Module {i}: {title}")
        else:
            print(f"   ✓ Module {i} already exists")

if __name__ == "__main__":
    success = migrate_database()
    if success:
        print("\n🎯 Migration complete! Now run:")
        print("   cd backend && uvicorn app.main:app --reload")
    else:
        print("\n❌ Migration failed. Check errors above.")
