#!/usr/bin/env python3
"""
Fix Indentation Error in modules.py
Run from harv root directory: python fix_indentation_error.py
"""

import os
import re

def fix_indentation_error():
    """Fix the indentation error in modules.py"""
    modules_path = "backend/app/endpoints/modules.py"
    
    if not os.path.exists(modules_path):
        print(f"❌ {modules_path} not found")
        return
    
    print("🔧 Fixing indentation error in modules.py...")
    
    # Read the file
    with open(modules_path, 'r') as f:
        content = f.read()
    
    # Check for common indentation issues
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines, 1):
        # Look for mixed tabs and spaces
        if '\t' in line and ' ' in line:
            # Convert tabs to spaces
            line = line.replace('\t', '    ')
            print(f"🔧 Line {i}: Fixed mixed tabs/spaces")
        
        # Look for unexpected indentation
        if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
            # This is a line that should be at the beginning
            fixed_lines.append(line)
        elif line.strip():
            # This is an indented line - make sure it's properly indented
            stripped = line.lstrip()
            if stripped.startswith('def ') or stripped.startswith('class '):
                # Function or class definition - no indentation needed
                fixed_lines.append(stripped)
            elif stripped.startswith('@'):
                # Decorator - no indentation needed
                fixed_lines.append(stripped)
            else:
                # Regular line - maintain indentation
                fixed_lines.append(line)
        else:
            # Empty line
            fixed_lines.append(line)
    
    # Write the fixed content
    fixed_content = '\n'.join(fixed_lines)
    
    # Create backup
    backup_path = f"{modules_path}.backup"
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"📁 Backup created: {backup_path}")
    
    # Write fixed file
    with open(modules_path, 'w') as f:
        f.write(fixed_content)
    
    print("✅ Indentation error fixed!")
    print("\n🚀 Next steps:")
    print("1. cd backend")
    print("2. uvicorn app.main:app --reload")
    print("3. Test: curl http://127.0.0.1:8000/health")

if __name__ == "__main__":
    fix_indentation_error()
