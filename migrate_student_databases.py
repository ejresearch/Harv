#!/usr/bin/env python3
"""
HARV CLI Database Migration Script
Upgrades existing student databases to include enhanced security features
"""

import os
import sqlite3
import sys
from datetime import datetime
import getpass


class DatabaseMigrator:
    """Handles migration of legacy student databases"""
    
    def __init__(self):
        self.students_dir = "students"
        self.migrated_count = 0
        self.failed_count = 0
    
    def find_legacy_databases(self):
        """Find student databases that need migration"""
        if not os.path.exists(self.students_dir):
            return []
        
        legacy_dbs = []
        
        for entry in os.scandir(self.students_dir):
            if entry.is_dir():
                db_path = os.path.join(entry.path, f"{entry.name}_harv.sqlite")
                if os.path.exists(db_path):
                    if self.needs_migration(db_path):
                        legacy_dbs.append((entry.name, db_path))
        
        return legacy_dbs
    
    def needs_migration(self, db_path):
        """Check if database needs migration"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if auth table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='student_auth'"
            )
            auth_table_exists = cursor.fetchone() is not None
            
            # Check if learning_insights table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='learning_insights'"
            )
            insights_table_exists = cursor.fetchone() is not None
            
            conn.close()
            
            return not (auth_table_exists and insights_table_exists)
            
        except Exception as e:
            print(f"❌ Error checking database {db_path}: {e}")
            return False
    
    def migrate_database(self, student_name, db_path):
        """Migrate a single database"""
        print(f"🔄 Migrating database for {student_name}...")
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Add student_auth table if missing
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='student_auth'"
            )
            if not cursor.fetchone():
                print(f"  📋 Adding authentication table...")
                cursor.execute("""
                    CREATE TABLE student_auth (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_name TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP,
                        failed_attempts INTEGER DEFAULT 0,
                        locked_until TIMESTAMP
                    )
                """)
                
                # Prompt for password
                print(f"  🔑 Setting up password for {student_name}")
                while True:
                    try:
                        password = getpass.getpass(f"    Enter new password for {student_name}: ")
                        password_confirm = getpass.getpass(f"    Confirm password: ")
                    except (ImportError, OSError):
                        password = input(f"    Enter new password for {student_name}: ")
                        password_confirm = input(f"    Confirm password: ")
                    
                    if password != password_confirm:
                        print("    ❌ Passwords don't match. Try again.")
                        continue
                    
                    if len(password) < 8:
                        print("    ❌ Password must be at least 8 characters long.")
                        continue
                    
                    break
                
                # Hash password (simple version for migration)
                import hashlib
                import secrets
                import base64
                
                salt = secrets.token_bytes(32)
                password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
                stored_hash = base64.b64encode(salt + password_hash).decode()
                
                cursor.execute(
                    "INSERT INTO student_auth (student_name, password_hash) VALUES (?, ?)",
                    (student_name, stored_hash)
                )
                
                print(f"  ✅ Authentication configured")
            
            # Add learning_insights table if missing
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='learning_insights'"
            )
            if not cursor.fetchone():
                print(f"  🧠 Adding learning insights table...")
                cursor.execute("""
                    CREATE TABLE learning_insights (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        module_id INTEGER NOT NULL,
                        insight_text TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                print(f"  ✅ Learning insights table added")
            
            # Update conversations table if needed
            cursor.execute("PRAGMA table_info(conversations)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'session_id' not in columns:
                print(f"  📝 Updating conversations table...")
                cursor.execute("ALTER TABLE conversations ADD COLUMN session_id TEXT")
            
            if 'created_at' not in columns:
                cursor.execute("ALTER TABLE conversations ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            
            # Add migration metadata
            cursor.execute(
                "INSERT OR REPLACE INTO student_metadata (key, value) VALUES ('migrated_at', ?)",
                (datetime.now().isoformat(),)
            )
            cursor.execute(
                "INSERT OR REPLACE INTO student_metadata (key, value) VALUES ('migration_version', '2.0')",
            )
            
            conn.commit()
            conn.close()
            
            print(f"  ✅ Migration completed for {student_name}")
            self.migrated_count += 1
            return True
            
        except Exception as e:
            print(f"  ❌ Migration failed for {student_name}: {e}")
            self.failed_count += 1
            return False
    
    def create_backup(self, db_path):
        """Create backup of database before migration"""
        backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            import shutil
            shutil.copy2(db_path, backup_path)
            print(f"  💾 Backup created: {backup_path}")
            return True
        except Exception as e:
            print(f"  ❌ Failed to create backup: {e}")
            return False
    
    def run_migration(self):
        """Run complete migration process"""
        print("🚀 HARV CLI Database Migration Tool")
        print("=" * 50)
        
        legacy_dbs = self.find_legacy_databases()
        
        if not legacy_dbs:
            print("✅ No databases require migration!")
            return
        
        print(f"📊 Found {len(legacy_dbs)} database(s) requiring migration:")
        for student_name, db_path in legacy_dbs:
            print(f"  • {student_name}: {db_path}")
        
        print("\n⚠️  This will modify your student databases.")
        print("   Backups will be created automatically.")
        
        confirm = input(f"\nProceed with migration? (y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ Migration cancelled")
            return
        
        print("\n🔄 Starting migration process...")
        
        for student_name, db_path in legacy_dbs:
            print(f"\n📋 Processing {student_name}...")
            
            # Create backup
            if self.create_backup(db_path):
                # Perform migration
                self.migrate_database(student_name, db_path)
            else:
                print(f"  ⚠️  Skipping {student_name} due to backup failure")
                self.failed_count += 1
        
        print("\n" + "=" * 50)
        print("📊 MIGRATION SUMMARY")
        print(f"✅ Successfully migrated: {self.migrated_count}")
        print(f"❌ Failed migrations: {self.failed_count}")
        
        if self.failed_count == 0:
            print("\n🎉 All databases migrated successfully!")
            print("🔒 Enhanced security features are now available")
        else:
            print(f"\n⚠️  {self.failed_count} migration(s) failed")
            print("   Please check the error messages above")


def verify_migration():
    """Verify migration completed successfully"""
    print("\n🔍 Verifying migration...")
    
    migrator = DatabaseMigrator()
    legacy_dbs = migrator.find_legacy_databases()
    
    if not legacy_dbs:
        print("✅ All databases are up to date!")
        return True
    else:
        print(f"❌ {len(legacy_dbs)} database(s) still need migration")
        return False


if __name__ == '__main__':
    migrator = DatabaseMigrator()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--verify':
        verify_migration()
    else:
        migrator.run_migration()
        verify_migration()