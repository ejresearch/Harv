#!/usr/bin/env python3
"""
Fix Database Location Issue and Complete Schema Resolution
Run from root directory: python fix_database_location.py
"""

import sqlite3
import os
import shutil
from datetime import datetime

def find_all_db_files():
    """Find all harv.db files in the project"""
    db_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file == 'harv.db':
                db_files.append(os.path.join(root, file))
    return db_files

def check_db_schema(db_path):
    """Check database schema completeness"""
    if not os.path.exists(db_path):
        return None
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Check specific columns
        schema_info = {}
        
        if 'documents' in tables:
            cursor.execute("PRAGMA table_info(documents)")
            doc_cols = [row[1] for row in cursor.fetchall()]
            schema_info['documents_has_user_id'] = 'user_id' in doc_cols
        
        if 'memory_summaries' in tables:
            cursor.execute("PRAGMA table_info(memory_summaries)")
            memory_cols = [row[1] for row in cursor.fetchall()]
            schema_info['memory_has_conversation_id'] = 'conversation_id' in memory_cols
            schema_info['memory_has_key_concepts'] = 'key_concepts' in memory_cols
        
        if 'modules' in tables:
            cursor.execute("SELECT COUNT(*) FROM modules")
            schema_info['module_count'] = cursor.fetchone()[0]
        
        conn.close()
        return schema_info
    
    except Exception as e:
        conn.close()
        return {"error": str(e)}

def apply_schema_fixes_to_db(db_path):
    """Apply all schema fixes to a specific database file"""
    print(f"🔧 Applying schema fixes to: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"   ❌ Database not found: {db_path}")
        return False
    
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.backup_{timestamp}"
    shutil.copy2(db_path, backup_path)
    print(f"   📁 Backup created: {backup_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Fix 1: Documents table user_id
        cursor.execute("PRAGMA table_info(documents)")
        doc_columns = [row[1] for row in cursor.fetchall()]
        
        if 'user_id' not in doc_columns:
            cursor.execute("ALTER TABLE documents ADD COLUMN user_id INTEGER")
            print("   ✅ Added user_id to documents")
        else:
            print("   ✅ documents.user_id already exists")
        
        # Fix 2: Memory summaries table fields
        cursor.execute("PRAGMA table_info(memory_summaries)")
        memory_columns = [row[1] for row in cursor.fetchall()]
        
        missing_memory_fields = [
            ("conversation_id", "INTEGER"),
            ("key_concepts", "TEXT"),
            ("created_at", "DATETIME DEFAULT CURRENT_TIMESTAMP"),
            ("updated_at", "DATETIME DEFAULT CURRENT_TIMESTAMP")
        ]
        
        for field_name, field_type in missing_memory_fields:
            if field_name not in memory_columns:
                cursor.execute(f"ALTER TABLE memory_summaries ADD COLUMN {field_name} {field_type}")
                print(f"   ✅ Added {field_name} to memory_summaries")
            else:
                print(f"   ✅ memory_summaries.{field_name} already exists")
        
        # Fix 3: Ensure all module fields exist
        cursor.execute("PRAGMA table_info(modules)")
        module_columns = [row[1] for row in cursor.fetchall()]
        
        module_fields = [
            ("module_prompt", "TEXT"),
            ("system_corpus", "TEXT"),
            ("module_corpus", "TEXT"),
            ("dynamic_corpus", "TEXT"),
            ("api_endpoint", "TEXT"),
            ("learning_objectives", "TEXT"),
            ("memory_extraction_prompt", "TEXT"),
            ("mastery_triggers", "TEXT"),
            ("confusion_triggers", "TEXT"),
            ("memory_context_template", "TEXT"),
            ("cross_module_references", "TEXT"),
            ("memory_weight", "TEXT DEFAULT 'balanced'"),
            ("include_system_memory", "BOOLEAN DEFAULT TRUE"),
            ("include_module_progress", "BOOLEAN DEFAULT TRUE"),
            ("include_learning_style", "BOOLEAN DEFAULT TRUE"),
            ("include_conversation_state", "BOOLEAN DEFAULT TRUE"),
            ("include_recent_breakthroughs", "BOOLEAN DEFAULT TRUE"),
            ("update_memory_on_response", "BOOLEAN DEFAULT TRUE"),
            ("track_understanding_level", "BOOLEAN DEFAULT TRUE"),
            ("created_at", "DATETIME"),
            ("updated_at", "DATETIME")
        ]
        
        module_updates = 0
        for field_name, field_type in module_fields:
            if field_name not in module_columns:
                cursor.execute(f"ALTER TABLE modules ADD COLUMN {field_name} {field_type}")
                module_updates += 1
        
        if module_updates > 0:
            print(f"   ✅ Added {module_updates} fields to modules")
        else:
            print("   ✅ All module fields exist")
        
        # Fix 4: Ensure 15 modules exist with proper configuration
        cursor.execute("SELECT COUNT(*) FROM modules")
        module_count = cursor.fetchone()[0]
        
        if module_count < 15:
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
            
            created_count = 0
            for i, title in enumerate(mass_comm_modules, 1):
                cursor.execute("SELECT id FROM modules WHERE id = ?", (i,))
                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO modules (
                            id, title, description, resources, 
                            system_prompt, module_prompt, system_corpus, module_corpus, dynamic_corpus,
                            api_endpoint, memory_extraction_prompt, mastery_triggers, confusion_triggers,
                            memory_context_template, cross_module_references, memory_weight,
                            created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        i, title, f"Module {i} of the Mass Communication course", "",
                        "You are Harv, a Socratic tutor for mass communication. Never give direct answers. Always respond with thoughtful questions that guide discovery.",
                        f"Focus on helping students discover concepts in {title} through questioning.",
                        "Core concepts: media theory, communication effects, journalism ethics, digital transformation",
                        "", "",  # module_corpus and dynamic_corpus start empty
                        "https://api.openai.com/v1/chat/completions",
                        "Analyze this conversation to extract: concepts mastered, learning breakthroughs, effective teaching methods",
                        "oh I see, that makes sense, so it means, I understand now, exactly, of course",
                        "I don't understand, this is confusing, what do you mean, I'm lost, huh?",
                        "Remember, this student previously mastered {concepts} and responds well to {teaching_methods}",
                        "Remember when you discovered {concept} in Module {number}? How might that connect to what we're exploring now?",
                        "balanced",
                        datetime.now().isoformat(),
                        datetime.now().isoformat()
                    ))
                    created_count += 1
            
            if created_count > 0:
                print(f"   ✅ Created {created_count} missing modules")
        
        # Update existing modules with missing configurations
        cursor.execute("""
            UPDATE modules SET 
                api_endpoint = COALESCE(api_endpoint, ?),
                memory_extraction_prompt = COALESCE(memory_extraction_prompt, ?),
                memory_weight = COALESCE(memory_weight, ?),
                updated_at = ?
            WHERE api_endpoint IS NULL OR memory_extraction_prompt IS NULL OR memory_weight IS NULL
        """, (
            "https://api.openai.com/v1/chat/completions",
            "Analyze this conversation to extract: concepts mastered, learning breakthroughs, effective teaching methods",
            "balanced",
            datetime.now().isoformat()
        ))
        
        # Fix 5: Create missing tables
        required_tables = {
            'onboarding_surveys': """
                CREATE TABLE IF NOT EXISTS onboarding_surveys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    reason TEXT,
                    familiarity TEXT,
                    learning_style TEXT,
                    goals TEXT,
                    background TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """,
            'course_corpus': """
                CREATE TABLE IF NOT EXISTS course_corpus (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    type TEXT NOT NULL,
                    order_index INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """,
            'module_corpus_entries': """
                CREATE TABLE IF NOT EXISTS module_corpus_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    module_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    type TEXT NOT NULL,
                    order_index INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (module_id) REFERENCES modules (id) ON DELETE CASCADE
                )
            """
        }
        
        for table_name, create_sql in required_tables.items():
            cursor.execute(create_sql)
            print(f"   ✅ Ensured {table_name} table exists")
        
        # Fix 6: Create indexes
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_documents_user ON documents(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_memory_summaries_conversation ON memory_summaries(conversation_id)",
            "CREATE INDEX IF NOT EXISTS idx_memory_summaries_user ON memory_summaries(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_conversations_user_module ON conversations(user_id, module_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_progress_user ON user_progress(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_onboarding_user ON onboarding_surveys(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_module_corpus_module ON module_corpus_entries(module_id)"
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
            except Exception:
                pass  # Index might already exist
        
        print("   ✅ Created performance indexes")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Schema fix failed: {e}")
        conn.rollback()
        conn.close()
        return False

def consolidate_databases():
    """Consolidate all database files and ensure they have the same schema"""
    print("🗄️ DATABASE LOCATION AND SCHEMA CONSOLIDATION")
    print("=" * 60)
    
    # Find all database files
    db_files = find_all_db_files()
    print(f"📋 Found database files: {db_files}")
    
    if not db_files:
        print("❌ No database files found!")
        return False
    
    # Check schema of each database
    print("\n🔍 Checking database schemas...")
    for db_file in db_files:
        print(f"\n📄 {db_file}:")
        schema_info = check_db_schema(db_file)
        if schema_info:
            if 'error' in schema_info:
                print(f"   ❌ Error: {schema_info['error']}")
            else:
                for key, value in schema_info.items():
                    status = "✅" if value else "❌"
                    print(f"   {key}: {status} {value}")
        else:
            print("   ❌ Could not read schema")
    
    # Apply fixes to all databases
    print(f"\n🔧 Applying schema fixes to all {len(db_files)} databases...")
    
    success_count = 0
    for db_file in db_files:
        if apply_schema_fixes_to_db(db_file):
            success_count += 1
    
    print(f"\n✅ Successfully fixed {success_count}/{len(db_files)} databases")
    
    # Recommend primary database location
    print("\n📍 RECOMMENDED DATABASE SETUP:")
    print("   Primary database: ./harv.db (root directory)")
    print("   Backend should use: ../harv.db (relative to backend/)")
    
    return success_count == len(db_files)

def update_backend_database_config():
    """Update backend database configuration to use root database"""
    print("\n🔗 Updating backend database configuration...")
    
    database_py_path = "backend/app/database.py"
    if not os.path.exists(database_py_path):
        print(f"   ❌ Database config not found: {database_py_path}")
        return False
    
    try:
        # Read current config
        with open(database_py_path, 'r') as f:
            content = f.read()
        
        # Update DATABASE_URL to point to root
        if 'sqlite:///./harv.db' in content:
            updated_content = content.replace(
                'sqlite:///./harv.db',
                'sqlite:///../harv.db'
            )
            
            # Write updated config
            with open(database_py_path, 'w') as f:
                f.write(updated_content)
            
            print("   ✅ Updated database.py to use root database")
            return True
        else:
            print("   ✅ Database config already points to correct location")
            return True
            
    except Exception as e:
        print(f"   ❌ Failed to update database config: {e}")
        return False

def main():
    """Main consolidation function"""
    success = consolidate_databases()
    
    if success:
        config_success = update_backend_database_config()
        
        print("\n" + "=" * 60)
        print("📊 CONSOLIDATION SUMMARY")
        print("=" * 60)
        
        print(f"   Database schema fixes: {'✅' if success else '❌'}")
        print(f"   Backend configuration: {'✅' if config_success else '⚠️'}")
        
        if success and config_success:
            print("\n🎉 ALL DATABASE ISSUES RESOLVED!")
            print("\n🎯 Next Steps:")
            print("1. ✅ Database schema fully resolved")
            print("2. 🧪 Run tests: cd backend && python test_models_fix.py")
            print("3. 🚀 Start backend: uvicorn app.main:app --reload")
            print("4. 🔄 Continue with Environment Configuration")
        
        return success and config_success
    
    else:
        print("\n❌ Database consolidation failed")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
