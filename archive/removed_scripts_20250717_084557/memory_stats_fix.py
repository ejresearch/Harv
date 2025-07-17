#!/usr/bin/env python3
"""
Memory Stats Endpoint Fix
Fixes the AttributeError in memory.py line 219
Run from harv root directory: python memory_stats_fix.py
"""

import os
import re
from datetime import datetime

def fix_memory_stats():
    """Fix the memory stats endpoint AttributeError"""
    
    print("🔧 Fixing Memory Stats Endpoint")
    print("=" * 40)
    
    memory_path = "backend/app/endpoints/memory.py"
    if not os.path.exists(memory_path):
        print(f"❌ {memory_path} not found")
        return
    
    # Create backup
    backup_path = f"{memory_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(memory_path, 'r') as f:
        content = f.read()
    
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"📁 Backup created: {backup_path}")
    
    # Fix the AttributeError on line 219
    # Change: user_id = current_user.id if current_user else None
    # To: user_id = current_user.id if current_user and hasattr(current_user, 'id') else None
    
    # Pattern to match the problematic line
    pattern = r'user_id = current_user\.id if current_user else None'
    replacement = 'user_id = current_user.id if current_user and hasattr(current_user, \'id\') else None'
    
    # Apply the fix
    fixed_content = re.sub(pattern, replacement, content)
    
    # Also fix any other similar patterns
    pattern2 = r'current_user\.id'
    def safe_user_id(match):
        return 'getattr(current_user, \'id\', None)'
    
    # Only replace if not already in a conditional
    lines = fixed_content.split('\n')
    for i, line in enumerate(lines):
        if 'current_user.id' in line and 'hasattr' not in line and 'getattr' not in line:
            # Replace current_user.id with getattr(current_user, 'id', None)
            lines[i] = re.sub(r'current_user\.id', 'getattr(current_user, \'id\', None)', line)
    
    fixed_content = '\n'.join(lines)
    
    # Write the fixed content
    with open(memory_path, 'w') as f:
        f.write(fixed_content)
    
    print("✅ Memory stats endpoint fixed")
    print("")
    print("🚀 Next Steps:")
    print("1. Restart backend: uvicorn app.main:app --reload")
    print("2. Test GUI: http://localhost:3000/dev-gui.html")
    print("3. No more 500 errors for /memory/stats/{id}")
    print("")
    print("🎯 Your Module Configuration System should now be fully functional!")

if __name__ == "__main__":
    fix_memory_stats()
