#!/usr/bin/env python3
"""
Memory System Migration Script
Place this file in your ROOT directory (same level as README.md)
Run: python memory_migration.py
"""

import sqlite3
import os
import shutil
from datetime import datetime

def add_memory_fields():
    """Add memory-related fields to existing database"""
    print("🧠 MEMORY SYSTEM MIGRATION")
    print("=" * 40)
    
    db_file = "harv.db"
    if not os.path.exists(db_file):
        print("❌ Database file not found. Run the backend first.")
        return False
    
    # Create backup
    backup_file = f"harv_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy2(db_file, backup_file)
    print(f"📁 Created backup: {backup_file}")
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    try:
        # Add memory fields to modules table
        print("📚 Adding memory fields to modules table...")
        
        memory_fields = [
            "ALTER TABLE modules ADD COLUMN memory_extraction_prompt TEXT",
            "ALTER TABLE modules ADD COLUMN mastery_triggers TEXT",
            "ALTER TABLE modules ADD COLUMN confusion_triggers TEXT", 
            "ALTER TABLE modules ADD COLUMN memory_context_template TEXT",
            "ALTER TABLE modules ADD COLUMN cross_module_references TEXT",
            "ALTER TABLE modules ADD COLUMN memory_weight TEXT DEFAULT 'balanced'",
            "ALTER TABLE modules ADD COLUMN include_system_memory BOOLEAN DEFAULT TRUE",
            "ALTER TABLE modules ADD COLUMN include_module_progress BOOLEAN DEFAULT TRUE",
            "ALTER TABLE modules ADD COLUMN track_understanding_level BOOLEAN DEFAULT TRUE"
        ]
        
        for sql in memory_fields:
            try:
                cursor.execute(sql)
                field_name = sql.split("ADD COLUMN ")[1].split(" ")[0]
                print(f"   ✅ Added {field_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    field_name = sql.split("ADD COLUMN ")[1].split(" ")[0]
                    print(f"   ⚠️ {field_name} already exists")
                else:
                    print(f"   ❌ Error: {e}")
        
        # Add memory fields to memory_summaries table
        print("🧠 Adding fields to memory_summaries table...")
        
        memory_summary_fields = [
            "ALTER TABLE memory_summaries ADD COLUMN learning_insights TEXT",
            "ALTER TABLE memory_summaries ADD COLUMN teaching_effectiveness TEXT"
        ]
        
        for sql in memory_summary_fields:
            try:
                cursor.execute(sql)
                field_name = sql.split("ADD COLUMN ")[1].split(" ")[0]
                print(f"   ✅ Added {field_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    field_name = sql.split("ADD COLUMN ")[1].split(" ")[0]
                    print(f"   ⚠️ {field_name} already exists")
                else:
                    print(f"   ❌ Error: {e}")
        
        # Create course_corpus table if it doesn't exist
        print("📖 Creating course_corpus table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS course_corpus (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                type TEXT NOT NULL,
                order_index INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("   ✅ course_corpus table ready")
        
        # Create module_corpus_entries table if it doesn't exist
        print("📚 Creating module_corpus_entries table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS module_corpus_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                type TEXT NOT NULL,
                order_index INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (module_id) REFERENCES modules (id)
            )
        """)
        print("   ✅ module_corpus_entries table ready")
        
        conn.commit()
        print("✅ Memory system migration completed!")
        
        # Verify tables
        print("\n🔍 Verifying migration...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['users', 'modules', 'conversations', 'memory_summaries', 
                          'course_corpus', 'module_corpus_entries']
        
        for table in required_tables:
            if table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"   ✅ {table}: {count} records")
            else:
                print(f"   ❌ Missing: {table}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        conn.close()
        return False

if __name__ == "__main__":
    success = add_memory_fields()
    if success:
        print("\n🎯 Next steps:")
        print("1. Start backend: cd backend && uvicorn app.main:app --reload")
        print("2. Test memory system in GUI: http://localhost:3000/dev-gui.html")
        print("3. Use Memory System tab to configure memory extraction")
    else:
        print("\n❌ Migration failed. Check errors above.")
