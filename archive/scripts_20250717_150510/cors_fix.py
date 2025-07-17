#!/usr/bin/env python3
"""
CORS Fix for Port 3001
Updates backend CORS to allow demo frontend on port 3001
Run from harv root: python cors_fix.py
"""

import os
import re
from datetime import datetime

def fix_cors_configuration():
    """Fix CORS to allow demo frontend on port 3001"""
    print("🔧 CORS Fix - Allow Demo Frontend on Port 3001")
    print("=" * 50)
    
    main_py_path = "backend/app/main.py"
    
    if not os.path.exists(main_py_path):
        print(f"❌ File not found: {main_py_path}")
        return False
    
    # Backup current file
    backup_name = f"backend/app/main.py.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(main_py_path, 'r') as f:
        content = f.read()
    
    with open(backup_name, 'w') as f:
        f.write(content)
    print(f"📁 Backup created: {backup_name}")
    
    # Find and update CORS configuration
    cors_pattern = r'allow_origins=\[(.*?)\]'
    
    if re.search(cors_pattern, content, re.DOTALL):
        # Update existing CORS configuration
        new_cors = '''allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000", 
        "http://localhost:3001",  # Demo frontend
        "http://127.0.0.1:3001",  # Demo frontend
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:5173"
    ]'''
        
        content = re.sub(cors_pattern, new_cors, content, flags=re.DOTALL)
        print("✅ Updated existing CORS configuration")
        
    else:
        print("⚠️  CORS configuration not found in expected format")
        return False
    
    # Write updated content
    with open(main_py_path, 'w') as f:
        f.write(content)
    
    print("✅ CORS configuration updated")
    print("")
    print("📋 Updated CORS to allow:")
    print("   ✅ http://localhost:3000 (GUI)")
    print("   ✅ http://localhost:3001 (Demo)")
    print("   ✅ http://localhost:5173 (React)")
    print("   ✅ All 127.0.0.1 variants")
    print("")
    print("🚀 Next steps:")
    print("   1. Restart your backend")
    print("   2. Refresh your demo page")
    print("   3. Should see '✅ Backend Connected'")
    
    return True

def create_restart_script():
    """Create a script to restart backend and demo"""
    restart_script = '''#!/bin/bash
# Restart Backend and Demo
echo "🔄 Restarting Backend and Demo..."

# Kill existing backend processes
pkill -f "uvicorn app.main:app"

# Start backend with updated CORS
echo "🚀 Starting backend with updated CORS..."
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"

# Wait for backend to start
sleep 3

# Test backend
if curl -s http://127.0.0.1:8000/health > /dev/null; then
    echo "✅ Backend health check passed"
else
    echo "❌ Backend health check failed"
fi

echo ""
echo "🎯 Demo should now show '✅ Backend Connected'"
echo "   Demo URL: http://localhost:3001"
echo "   Backend:  http://127.0.0.1:8000"
echo ""
echo "💡 If demo still shows 'Backend Not Connected':"
echo "   - Force refresh: Ctrl+F5 (or Cmd+Shift+R)"
echo "   - Check browser console (F12) for errors"
'''
    
    with open("restart_backend_demo.sh", "w") as f:
        f.write(restart_script)
    
    os.chmod("restart_backend_demo.sh", 0o755)
    print("📝 Created restart script: restart_backend_demo.sh")

if __name__ == "__main__":
    if fix_cors_configuration():
        create_restart_script()
        print("")
        print("🎯 CORS FIX COMPLETE!")
        print("=" * 20)
        print("")
        print("Run this to restart with new CORS settings:")
        print("   bash restart_backend_demo.sh")
        print("")
        print("Or manually restart backend:")
        print("   cd backend")
        print("   uvicorn app.main:app --reload")
    else:
        print("❌ CORS fix failed - manual update needed")
