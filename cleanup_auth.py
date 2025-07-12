#!/usr/bin/env python3
"""
Remove conflicting authentication files
Run: python cleanup_auth.py
"""

import os
import shutil

def cleanup_auth_conflicts():
    """Remove conflicting auth files"""
    print("🧹 CLEANING UP AUTH CONFLICTS")
    print("=" * 40)
    
    files_to_remove = [
        "backend/app/auth_working.py",
        "backend/app/endpoints/auth.py.bak", 
        "backend/temp_auth_fix.py",
        "backend/temp_fix.py",
        "backend/temp_model.py",
        "backend/fix_auth_dependency.py"
    ]
    
    removed_count = 0
    
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"✅ Removed: {file_path}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Failed to remove {file_path}: {e}")
        else:
            print(f"⚪ Not found: {file_path}")
    
    print(f"\n🎯 Cleanup complete! Removed {removed_count} conflicting files.")
    
    # Verify main auth file exists
    if os.path.exists("backend/app/auth.py"):
        print("✅ Main auth.py file exists - good!")
    else:
        print("❌ Main auth.py file missing - this is a problem!")
        return False
    
    return True

if __name__ == "__main__":
    success = cleanup_auth_conflicts()
    if success:
        print("\n🎉 Auth cleanup successful!")
        print("Now run: python fix_database.py")
    else:
        print("\n❌ Auth cleanup failed!")
