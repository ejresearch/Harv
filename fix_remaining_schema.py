#!/usr/bin/env python3
"""
Fix Remaining Database Schema Issues
Run: python fix_remaining_schema.py
"""

import sqlite3
import os
from datetime import datetime

def fix_remaining_schema_issues():
    """Fix the remaining schema issues identified in tests"""
    print("🔧 FIXING REMAINING SCHEMA ISSUES")
    print("=" * 50)
    
    db_path = "harv.db"
    if not os.path.exists(db_path):
        print("❌ Database file not found")
        return False
    
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.backup_{timestamp}"
    import shutil
    shutil.copy2(db_path, backup_path)
    print(f"📁 Created backup: {backup_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Fix 1: Add user_id to documents table
        print("1. 📄 Fixing documents table...")
        cursor.execute("PRAGMA table_info(documents)")
        doc_columns = [row[1] for row in cursor.fetchall()]
        print(f"   Current documents columns: {doc_columns}")
        
        if 'user_id' not in doc_columns:
            cursor.execute("ALTER TABLE documents ADD COLUMN user_id INTEGER")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_user ON documents(user_id)")
            print("   ✅ Added user_id column to documents")
        else:
            print("   ✅ user_id already exists in documents")
        
        # Fix 2: Add conversation_id to memory_summaries table
        print("\n2. 🧠 Fixing memory_summaries table...")
        cursor.execute("PRAGMA table_info(memory_summaries)")
        memory_columns = [row[1] for row in cursor.fetchall()]
        print(f"   Current memory_summaries columns: {memory_columns}")
        
        if 'conversation_id' not in memory_columns:
            cursor.execute("ALTER TABLE memory_summaries ADD COLUMN conversation_id INTEGER")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_memory_summaries_conversation ON memory_summaries(conversation_id)")
            print("   ✅ Added conversation_id column to memory_summaries")
        else:
            print("   ✅ conversation_id already exists in memory_summaries")
        
        # Fix 3: Add any other missing fields to memory_summaries
        missing_memory_fields = [
            ("key_concepts", "TEXT"),
            ("created_at", "DATETIME DEFAULT CURRENT_TIMESTAMP"),
            ("updated_at", "DATETIME DEFAULT CURRENT_TIMESTAMP")
        ]
        
        for field_name, field_type in missing_memory_fields:
            if field_name not in memory_columns:
                try:
                    cursor.execute(f"ALTER TABLE memory_summaries ADD COLUMN {field_name} {field_type}")
                    print(f"   ✅ Added {field_name} to memory_summaries")
                except sqlite3.OperationalError as e:
                    print(f"   ⚠️  {field_name}: {e}")
        
        conn.commit()
        
        # Verification
        print("\n🔍 VERIFICATION")
        print("=" * 30)
        
        # Test documents table
        cursor.execute("PRAGMA table_info(documents)")
        doc_columns_after = [row[1] for row in cursor.fetchall()]
        has_user_id = 'user_id' in doc_columns_after
        print(f"   Documents user_id: {'✅' if has_user_id else '❌'}")
        
        # Test memory_summaries table
        cursor.execute("PRAGMA table_info(memory_summaries)")
        memory_columns_after = [row[1] for row in cursor.fetchall()]
        has_conversation_id = 'conversation_id' in memory_columns_after
        has_key_concepts = 'key_concepts' in memory_columns_after
        print(f"   Memory conversation_id: {'✅' if has_conversation_id else '❌'}")
        print(f"   Memory key_concepts: {'✅' if has_key_concepts else '❌'}")
        
        conn.close()
        
        print("\n✅ SCHEMA FIXES COMPLETED!")
        print(f"💾 Backup saved at: {backup_path}")
        return True
        
    except Exception as e:
        print(f"❌ Schema fix failed: {e}")
        conn.rollback()
        conn.close()
        return False

if __name__ == "__main__":
    success = fix_remaining_schema_issues()
    if success:
        print("\n🎯 Now run the tests again:")
        print("   cd backend")
        print("   python test_models_fix.py")
    else:
        print("\n❌ Fix failed")
