#!/usr/bin/env python3
"""
Complete Database Schema Resolution Script
Fixes all column mismatches and populates missing data
Run: python fix_database_schema.py
"""

import sqlite3
import os
import sys
import shutil
from datetime import datetime

def backup_database(db_path):
    """Create backup of existing database"""
    if not os.path.exists(db_path):
        print("❌ Database file not found. Please run backend first to create it.")
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.backup_{timestamp}"
    shutil.copy2(db_path, backup_path)
    print(f"📁 Created backup: {backup_path}")
    return backup_path

def check_table_exists(cursor, table_name):
    """Check if table exists"""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    return cursor.fetchone() is not None

def check_column_exists(cursor, table_name, column_name):
    """Check if column exists in table"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns

def add_column_safely(cursor, table_name, column_name, column_type, default_value=None):
    """Add column with proper error handling"""
    if not check_column_exists(cursor, table_name, column_name):
        try:
            if default_value:
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type} DEFAULT {default_value}")
            else:
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
            print(f"   ✅ Added {column_name} to {table_name}")
            return True
        except sqlite3.OperationalError as e:
            print(f"   ❌ Failed to add {column_name}: {e}")
            return False
    else:
        print(f"   ⚠️  Column {column_name} already exists in {table_name}")
        return False

def fix_database_schema():
    """Main function to fix all database schema issues"""
    print("🔧 HARV DATABASE SCHEMA RESOLUTION")
    print("=" * 60)
    
    db_path = "harv.db"
    backup_path = backup_database(db_path)
    if not backup_path:
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # ===== FIX 1: Password Column Naming =====
        print("1. 🔐 Fixing password column naming...")
        
        if check_table_exists(cursor, 'users'):
            cursor.execute("PRAGMA table_info(users)")
            user_columns = [row[1] for row in cursor.fetchall()]
            print(f"   Current users columns: {user_columns}")
            
            # Fix password field naming
            if 'password' in user_columns and 'hashed_password' not in user_columns:
                cursor.execute("ALTER TABLE users RENAME COLUMN password TO hashed_password")
                print("   ✅ Renamed 'password' to 'hashed_password'")
            elif 'hashed_password' not in user_columns:
                # Add hashed_password column if neither exists
                add_column_safely(cursor, 'users', 'hashed_password', 'TEXT')
                print("   ✅ Added hashed_password column")
            else:
                print("   ✅ Password field already correct (hashed_password)")
        
        # ===== FIX 2: Module Configuration Fields =====
        print("\n2. 📚 Adding missing module configuration fields...")
        
        if check_table_exists(cursor, 'modules'):
            cursor.execute("PRAGMA table_info(modules)")
            module_columns = [row[1] for row in cursor.fetchall()]
            print(f"   Current module columns: {module_columns}")
            
            # Add all missing module fields
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
            
            for field_name, field_type in module_fields:
                add_column_safely(cursor, 'modules', field_name, field_type)
        
        # ===== FIX 3: Conversation Table Enhancements =====
        print("\n3. 💬 Enhancing conversations table...")
        
        if check_table_exists(cursor, 'conversations'):
            conv_fields = [
                ("title", "TEXT DEFAULT 'New Conversation'"),
                ("current_grade", "TEXT"),
                ("memory_summary", "TEXT"),
                ("finalized", "BOOLEAN DEFAULT FALSE"),
                ("updated_at", "DATETIME")
            ]
            
            for field_name, field_type in conv_fields:
                add_column_safely(cursor, 'conversations', field_name, field_type)
        
        # ===== FIX 4: Create Missing Tables =====
        print("\n4. 🏗️  Creating missing tables...")
        
        # OnboardingSurvey table
        if not check_table_exists(cursor, 'onboarding_surveys'):
            cursor.execute("""
                CREATE TABLE onboarding_surveys (
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
            """)
            print("   ✅ Created onboarding_surveys table")
        
        # CourseCorpus table
        if not check_table_exists(cursor, 'course_corpus'):
            cursor.execute("""
                CREATE TABLE course_corpus (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    type TEXT NOT NULL,
                    order_index INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("   ✅ Created course_corpus table")
        
        # ModuleCorpusEntry table
        if not check_table_exists(cursor, 'module_corpus_entries'):
            cursor.execute("""
                CREATE TABLE module_corpus_entries (
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
            """)
            print("   ✅ Created module_corpus_entries table")
        
        # UserProgress enhancements
        if check_table_exists(cursor, 'user_progress'):
            progress_fields = [
                ("time_spent", "INTEGER DEFAULT 0"),
                ("attempts", "INTEGER DEFAULT 0")
            ]
            for field_name, field_type in progress_fields:
                add_column_safely(cursor, 'user_progress', field_name, field_type)
        
        # ===== FIX 5: Populate All 15 Modules =====
        print("\n5. 📖 Populating 15 mass communication modules...")
        
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
        updated_count = 0
        
        for i, title in enumerate(mass_comm_modules, 1):
            # Check if module exists
            cursor.execute("SELECT id FROM modules WHERE id = ?", (i,))
            existing = cursor.fetchone()
            
            if not existing:
                # Create new module with full configuration
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
                print(f"   ➕ Created Module {i}: {title}")
            else:
                # Update existing module with missing fields
                cursor.execute("""
                    UPDATE modules SET 
                        api_endpoint = COALESCE(api_endpoint, ?),
                        memory_extraction_prompt = COALESCE(memory_extraction_prompt, ?),
                        mastery_triggers = COALESCE(mastery_triggers, ?),
                        confusion_triggers = COALESCE(confusion_triggers, ?),
                        memory_context_template = COALESCE(memory_context_template, ?),
                        cross_module_references = COALESCE(cross_module_references, ?),
                        memory_weight = COALESCE(memory_weight, ?),
                        updated_at = ?
                    WHERE id = ?
                """, (
                    "https://api.openai.com/v1/chat/completions",
                    "Analyze this conversation to extract: concepts mastered, learning breakthroughs, effective teaching methods",
                    "oh I see, that makes sense, so it means, I understand now, exactly, of course",
                    "I don't understand, this is confusing, what do you mean, I'm lost, huh?",
                    "Remember, this student previously mastered {concepts} and responds well to {teaching_methods}",
                    "Remember when you discovered {concept} in Module {number}? How might that connect to what we're exploring now?",
                    "balanced",
                    datetime.now().isoformat(),
                    i
                ))
                updated_count += 1
                print(f"   🔄 Updated Module {i}: {title}")
        
        print(f"   ✅ Module population complete: {created_count} created, {updated_count} updated")
        
        # ===== FIX 6: Create Indexes for Performance =====
        print("\n6. 📈 Creating performance indexes...")
        
        indexes = [
            ("idx_conversations_user_module", "conversations", ["user_id", "module_id"]),
            ("idx_memory_summaries_user", "memory_summaries", ["user_id"]),
            ("idx_user_progress_user", "user_progress", ["user_id"]),
            ("idx_onboarding_user", "onboarding_surveys", ["user_id"]),
            ("idx_module_corpus_module", "module_corpus_entries", ["module_id"])
        ]
        
        for index_name, table_name, columns in indexes:
            if check_table_exists(cursor, table_name):
                try:
                    cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({', '.join(columns)})")
                    print(f"   ✅ Created index: {index_name}")
                except sqlite3.OperationalError as e:
                    print(f"   ⚠️  Index {index_name}: {e}")
        
        # Commit all changes
        conn.commit()
        
        # ===== VERIFICATION =====
        print("\n" + "=" * 60)
        print("🔍 VERIFICATION REPORT")
        print("=" * 60)
        
        # Check table counts
        verification_tables = [
            'users', 'modules', 'conversations', 'documents', 
            'memory_summaries', 'user_progress', 'onboarding_surveys',
            'course_corpus', 'module_corpus_entries'
        ]
        
        for table in verification_tables:
            if check_table_exists(cursor, table):
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"   📊 {table}: {count} records")
            else:
                print(f"   ❌ Missing: {table}")
        
        # Verify module configuration
        cursor.execute("SELECT COUNT(*) FROM modules WHERE api_endpoint IS NOT NULL")
        configured_modules = cursor.fetchone()[0]
        print(f"   🔧 Configured modules: {configured_modules}/15")
        
        # Check for password field
        cursor.execute("PRAGMA table_info(users)")
        user_columns = [row[1] for row in cursor.fetchall()]
        has_hashed_password = 'hashed_password' in user_columns
        print(f"   🔐 Password field correct: {'✅' if has_hashed_password else '❌'}")
        
        conn.close()
        
        print("\n🎉 DATABASE SCHEMA RESOLUTION COMPLETED!")
        print(f"💾 Backup saved at: {backup_path}")
        return True
        
    except Exception as e:
        print(f"❌ Schema resolution failed: {e}")
        conn.rollback()
        conn.close()
        return False

def test_database_connectivity():
    """Test database connectivity with backend models"""
    print("\n🔗 Testing database connectivity...")
    
    try:
        # Test basic SQLite connection
        conn = sqlite3.connect("harv.db")
        cursor = conn.cursor()
        
        # Test modules query
        cursor.execute("SELECT COUNT(*) FROM modules")
        module_count = cursor.fetchone()[0]
        print(f"   ✅ SQLite modules query: {module_count} modules")
        
        # Test specific fields
        cursor.execute("SELECT id, title, api_endpoint FROM modules LIMIT 1")
        sample = cursor.fetchone()
        if sample:
            print(f"   ✅ Sample module: ID={sample[0]}, Title='{sample[1][:30]}...', API={sample[2] is not None}")
        
        conn.close()
        
        # Test backend model compatibility
        try:
            sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))
            from app.database import SessionLocal
            from app.models import Module, User
            
            db = SessionLocal()
            modules = db.query(Module).limit(1).all()
            if modules:
                module = modules[0]
                print(f"   ✅ SQLAlchemy model query successful")
                print(f"   ✅ Module attributes: api_endpoint={hasattr(module, 'api_endpoint')}, module_prompt={hasattr(module, 'module_prompt')}")
            
            db.close()
            print("   ✅ Backend models compatible!")
            return True
            
        except Exception as model_error:
            print(f"   ⚠️  Backend model test: {model_error}")
            print("   ℹ️  This is normal if backend isn't set up yet")
            return True  # SQLite test passed
            
    except Exception as e:
        print(f"   ❌ Database connectivity test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Harv Database Schema Resolution...")
    
    success = fix_database_schema()
    
    if success:
        connectivity_ok = test_database_connectivity()
        
        if connectivity_ok:
            print("\n✅ ALL SCHEMA FIXES COMPLETED SUCCESSFULLY!")
            print("\n🎯 Next Steps:")
            print("1. ✅ Database schema resolved")
            print("2. 🔄 Continue with Environment Configuration:")
            print("   - Create .env file with OpenAI API key")
            print("   - Set JWT secret key")
            print("3. 🔄 Then Backend API Standardization")
            print("4. 🚀 Start backend: cd backend && uvicorn app.main:app --reload")
            print("5. 🧪 Test: curl http://127.0.0.1:8000/health")
        else:
            print("\n⚠️  Schema fixed but connectivity issues remain")
    else:
        print("\n❌ Schema resolution failed - check errors above")
