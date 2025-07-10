#!/usr/bin/env python3
"""
Enhanced Migration Script for Primer Initiative
Fixed SQLite DEFAULT CURRENT_TIMESTAMP issue
"""

import sqlite3
import os
import shutil
from datetime import datetime
from pathlib import Path

def backup_database(db_path):
    """Create a backup of the existing database"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.backup_{timestamp}"
    shutil.copy2(db_path, backup_path)
    return backup_path

def check_table_exists(cursor, table_name):
    """Check if a table exists"""
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name=?
    """, (table_name,))
    return cursor.fetchone() is not None

def check_column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns

def add_column_safely(cursor, table_name, column_name, column_type, default_value=None):
    """Add a column with proper SQLite handling"""
    if not check_column_exists(cursor, table_name, column_name):
        if default_value is not None:
            # For non-CURRENT_TIMESTAMP defaults
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type} DEFAULT {default_value}")
        else:
            # For columns that need special handling
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
            
        print(f"   ✅ Added {column_name} to {table_name}")
        return True
    else:
        print(f"   ⚠️  Column {column_name} already exists in {table_name}")
        return False

def migrate_existing_database(db_path):
    """Migrate existing database with backward compatibility"""
    
    # Create backup
    backup_path = backup_database(db_path)
    print(f"✅ Database backed up to: {backup_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Debug: Check existing schema
        print("🔍 Checking existing schema...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        print(f"   📋 Existing tables: {existing_tables}")
        
        # Check messages table structure
        if 'messages' in existing_tables:
            cursor.execute("PRAGMA table_info(messages)")
            messages_columns = [row[1] for row in cursor.fetchall()]
            print(f"   📋 Messages table columns: {messages_columns}")
        
        print("📝 Enhancing existing tables...")
        
        # 1. Enhance users table
        if check_table_exists(cursor, 'users'):
            # Add created_at with NULL first, then update
            if add_column_safely(cursor, 'users', 'created_at', 'DATETIME'):
                cursor.execute("UPDATE users SET created_at = datetime('now') WHERE created_at IS NULL")
            
            add_column_safely(cursor, 'users', 'reason', 'TEXT')
            add_column_safely(cursor, 'users', 'familiarity', 'TEXT')
            add_column_safely(cursor, 'users', 'learning_style', 'TEXT')
            add_column_safely(cursor, 'users', 'goals', 'TEXT')
            add_column_safely(cursor, 'users', 'background', 'TEXT')
            add_column_safely(cursor, 'users', 'updated_at', 'DATETIME')
            
            # Update updated_at for existing users
            cursor.execute("UPDATE users SET updated_at = datetime('now') WHERE updated_at IS NULL")
        
        # 2. Enhance modules table
        if check_table_exists(cursor, 'modules'):
            add_column_safely(cursor, 'modules', 'learning_objectives', 'TEXT')
            add_column_safely(cursor, 'modules', 'estimated_duration', 'INTEGER')
            add_column_safely(cursor, 'modules', 'difficulty_level', 'TEXT')
            add_column_safely(cursor, 'modules', 'prerequisites', 'TEXT')
            add_column_safely(cursor, 'modules', 'created_at', 'DATETIME')
            add_column_safely(cursor, 'modules', 'updated_at', 'DATETIME')
            
            # Update timestamps for existing modules
            cursor.execute("UPDATE modules SET created_at = datetime('now') WHERE created_at IS NULL")
            cursor.execute("UPDATE modules SET updated_at = datetime('now') WHERE updated_at IS NULL")
        
        # 3. Enhance conversations table
        if check_table_exists(cursor, 'conversations'):
            add_column_safely(cursor, 'conversations', 'title', 'TEXT')
            add_column_safely(cursor, 'conversations', 'current_grade', 'TEXT')
            add_column_safely(cursor, 'conversations', 'memory_summary', 'TEXT')
            add_column_safely(cursor, 'conversations', 'finalized', 'BOOLEAN', 'FALSE')
            add_column_safely(cursor, 'conversations', 'total_messages', 'INTEGER', '0')
            add_column_safely(cursor, 'conversations', 'last_activity', 'DATETIME')
            
            # Add created_at with special handling
            if add_column_safely(cursor, 'conversations', 'created_at', 'DATETIME'):
                cursor.execute("UPDATE conversations SET created_at = datetime('now') WHERE created_at IS NULL")
            
            # Update other fields for existing conversations
            cursor.execute("UPDATE conversations SET last_activity = datetime('now') WHERE last_activity IS NULL")
        
        # 4. Enhance messages table (only if it exists)
        if check_table_exists(cursor, 'messages'):
            add_column_safely(cursor, 'messages', 'message_type', 'TEXT', "'user'")
            add_column_safely(cursor, 'messages', 'tokens_used', 'INTEGER', '0')
            add_column_safely(cursor, 'messages', 'processing_time', 'REAL', '0.0')
            
            # Add created_at with special handling
            if add_column_safely(cursor, 'messages', 'created_at', 'DATETIME'):
                cursor.execute("UPDATE messages SET created_at = datetime('now') WHERE created_at IS NULL")
        else:
            print("   ⚠️  Messages table not found - will be created by application")
        
        # 5. Create new tables
        print("📦 Creating new tables...")
        
        # User Progress table
        if not check_table_exists(cursor, 'user_progress'):
            cursor.execute('''
                CREATE TABLE user_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    module_id INTEGER NOT NULL,
                    completed BOOLEAN DEFAULT FALSE,
                    grade TEXT,
                    completion_date DATETIME,
                    time_spent INTEGER DEFAULT 0,
                    attempts INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (module_id) REFERENCES modules (id),
                    UNIQUE(user_id, module_id)
                )
            ''')
            print("   ✅ Created user_progress table")
        
        # User Sessions table (for JWT)
        if not check_table_exists(cursor, 'user_sessions'):
            cursor.execute('''
                CREATE TABLE user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    refresh_token TEXT NOT NULL,
                    expires_at DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_used DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            print("   ✅ Created user_sessions table")
        
        # Memory Summaries table
        if not check_table_exists(cursor, 'memory_summaries'):
            cursor.execute('''
                CREATE TABLE memory_summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    module_id INTEGER,
                    conversation_id INTEGER,
                    summary_type TEXT NOT NULL,
                    summary_text TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (module_id) REFERENCES modules (id),
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                )
            ''')
            print("   ✅ Created memory_summaries table")
        
        # User Analytics table
        if not check_table_exists(cursor, 'user_analytics'):
            cursor.execute('''
                CREATE TABLE user_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    event_data TEXT,
                    module_id INTEGER,
                    conversation_id INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (module_id) REFERENCES modules (id),
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                )
            ''')
            print("   ✅ Created user_analytics table")
        
        # Onboarding Surveys table (missing table causing the error)
        if not check_table_exists(cursor, 'onboarding_surveys'):
            cursor.execute('''
                CREATE TABLE onboarding_surveys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    reason TEXT,
                    familiarity TEXT,
                    learning_style TEXT,
                    goals TEXT,
                    background TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            print("   ✅ Created onboarding_surveys table")
        
        # 6. Create indexes for performance
        print("📈 Creating indexes...")
        
        # Check what columns exist in each table before creating indexes
        def create_index_if_columns_exist(table_name, index_name, columns):
            # Get table info
            cursor.execute(f"PRAGMA table_info({table_name})")
            existing_columns = [row[1] for row in cursor.fetchall()]
            
            # Check if all required columns exist
            missing_columns = [col for col in columns if col not in existing_columns]
            
            if not missing_columns:
                index_sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({', '.join(columns)})"
                cursor.execute(index_sql)
                print(f"   ✅ Created index: {index_name}")
            else:
                print(f"   ⚠️  Skipped index {index_name} - missing columns: {missing_columns}")
        
        # New table indexes (these should work)
        new_table_indexes = [
            ("user_progress", "idx_user_progress_user_id", ["user_id"]),
            ("user_progress", "idx_user_progress_module_id", ["module_id"]),
            ("user_sessions", "idx_user_sessions_user_id", ["user_id"]),
            ("user_sessions", "idx_user_sessions_refresh_token", ["refresh_token"]),
            ("memory_summaries", "idx_memory_summaries_user_id", ["user_id"]),
            ("memory_summaries", "idx_memory_summaries_conversation_id", ["conversation_id"]),
            ("user_analytics", "idx_user_analytics_user_id", ["user_id"]),
            ("user_analytics", "idx_user_analytics_created_at", ["created_at"]),
        ]
        
        for table_name, index_name, columns in new_table_indexes:
            if check_table_exists(cursor, table_name):
                create_index_if_columns_exist(table_name, index_name, columns)
        
        # Existing table indexes (check columns first)
        existing_table_indexes = [
            ("conversations", "idx_conversations_user_id", ["user_id"]),
            ("conversations", "idx_conversations_created_at", ["created_at"]),
        ]
        
        # Only add message indexes if messages table exists
        if check_table_exists(cursor, 'messages'):
            existing_table_indexes.extend([
                ("messages", "idx_messages_conversation_id", ["conversation_id"]),
                ("messages", "idx_messages_created_at", ["created_at"]),
            ])
        
        for table_name, index_name, columns in existing_table_indexes:
            if check_table_exists(cursor, table_name):
                create_index_if_columns_exist(table_name, index_name, columns)
        
        print("   ✅ Created performance indexes")
        
        # 7. Update any existing data (only if tables exist)
        print("🔄 Updating existing data...")
        
        # Set default message types (only if messages table exists)
        if check_table_exists(cursor, 'messages'):
            cursor.execute("UPDATE messages SET message_type = 'user' WHERE message_type IS NULL AND sender = 'user'")
            cursor.execute("UPDATE messages SET message_type = 'assistant' WHERE message_type IS NULL AND sender = 'assistant'")
            cursor.execute("UPDATE messages SET message_type = 'system' WHERE message_type IS NULL AND sender = 'system'")
            print("   ✅ Updated message types")
        else:
            print("   ⚠️  Messages table not found - skipping message updates")
        
        # Update conversation titles based on first message (only if both tables exist)
        if check_table_exists(cursor, 'conversations') and check_table_exists(cursor, 'messages'):
            cursor.execute('''
                UPDATE conversations 
                SET title = (
                    SELECT SUBSTR(content, 1, 50) || '...' 
                    FROM messages 
                    WHERE messages.conversation_id = conversations.id 
                    AND messages.sender = 'user'
                    ORDER BY messages.id ASC 
                    LIMIT 1
                )
                WHERE title IS NULL
            ''')
            print("   ✅ Updated conversation titles")
        else:
            print("   ⚠️  Skipping conversation title updates - missing required tables")
        
        # Update total message counts (only if both tables exist)
        if check_table_exists(cursor, 'conversations') and check_table_exists(cursor, 'messages'):
            cursor.execute('''
                UPDATE conversations 
                SET total_messages = (
                    SELECT COUNT(*) 
                    FROM messages 
                    WHERE messages.conversation_id = conversations.id
                )
                WHERE total_messages = 0
            ''')
            print("   ✅ Updated message counts")
        else:
            print("   ⚠️  Skipping message count updates - missing required tables")
        
        conn.commit()
        print("✅ Migration completed successfully!")
        
        # 8. Verification
        print("\n🔍 Verifying migration...")
        
        # Check table counts
        tables_to_check = ['users', 'modules', 'conversations', 'messages', 'user_progress', 'user_sessions', 'memory_summaries', 'user_analytics', 'onboarding_surveys']
        for table in tables_to_check:
            if check_table_exists(cursor, table):
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"   📊 {table}: {count} records")
        
        print("\n🎉 Database migration completed successfully!")
        print(f"💾 Backup saved at: {backup_path}")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        raise e
    finally:
        conn.close()

def main():
    """Main migration function"""
    db_path = "harv.db"
    
    if os.path.exists(db_path):
        print(f"📦 Found existing database: {db_path}")
        print("🚀 Starting backward-compatible migration...")
        migrate_existing_database(db_path)
    else:
        print(f"❌ Database not found: {db_path}")
        print("Please run the application first to create the initial database.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎯 Next steps:")
        print("1. Start your FastAPI server: uvicorn app.main:app --reload")
        print("2. Test the health endpoint: curl http://127.0.0.1:8000/health")
        print("3. Run the complete test suite from your cURL commands")
    else:
        print("\n❌ Migration failed. Please check the errors above.")
