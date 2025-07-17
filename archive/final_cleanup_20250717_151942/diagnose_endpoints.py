#!/usr/bin/env python3
"""
Diagnose Endpoint Issues
Checks why the endpoints aren't loading properly
Run from harv root directory: python diagnose_endpoints.py
"""

import os
import sys
import subprocess

def check_file_syntax():
    """Check syntax of modules.py and memory.py"""
    print("🔍 Checking file syntax...")
    
    files_to_check = [
        "backend/app/endpoints/modules.py",
        "backend/app/endpoints/memory.py",
        "backend/app/main.py"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            try:
                # Try to compile the file
                with open(file_path, 'r') as f:
                    content = f.read()
                
                compile(content, file_path, 'exec')
                print(f"✅ {file_path} - Syntax OK")
                
            except SyntaxError as e:
                print(f"❌ {file_path} - Syntax Error: {e}")
                print(f"   Line {e.lineno}: {e.text}")
                
            except Exception as e:
                print(f"⚠️  {file_path} - Error: {e}")
        else:
            print(f"❌ {file_path} - File not found")

def check_endpoint_content():
    """Check if endpoints were actually added"""
    print("\n🔍 Checking endpoint content...")
    
    # Check modules.py
    modules_path = "backend/app/endpoints/modules.py"
    if os.path.exists(modules_path):
        with open(modules_path, 'r') as f:
            content = f.read()
        
        if "/{module_id}/config" in content:
            print("✅ Config endpoints found in modules.py")
        else:
            print("❌ Config endpoints NOT found in modules.py")
        
        # Check for required imports
        required_imports = ["from fastapi import", "from sqlalchemy.orm import", "HTTPException"]
        missing_imports = []
        
        for imp in required_imports:
            if imp not in content:
                missing_imports.append(imp)
        
        if missing_imports:
            print(f"⚠️  Missing imports in modules.py: {missing_imports}")
        else:
            print("✅ Required imports present in modules.py")
    
    # Check memory.py
    memory_path = "backend/app/endpoints/memory.py"
    if os.path.exists(memory_path):
        with open(memory_path, 'r') as f:
            content = f.read()
        
        if "/context/{user_id}" in content:
            print("✅ Context endpoint found in memory.py")
        else:
            print("❌ Context endpoint NOT found in memory.py")

def check_fastapi_routes():
    """Check if FastAPI is actually registering the routes"""
    print("\n🔍 Checking FastAPI route registration...")
    
    try:
        # Try to import the modules and check routes
        sys.path.append('backend')
        
        try:
            from app.endpoints.modules import router as modules_router
            print("✅ Modules router imported successfully")
            
            # Check if routes are registered
            routes = [route.path for route in modules_router.routes]
            print(f"   Routes found: {routes}")
            
            if "/{module_id}/config" in str(routes):
                print("✅ Config routes registered in modules router")
            else:
                print("❌ Config routes NOT registered in modules router")
                
        except Exception as e:
            print(f"❌ Failed to import modules router: {e}")
        
        try:
            from app.endpoints.memory import router as memory_router
            print("✅ Memory router imported successfully")
            
            routes = [route.path for route in memory_router.routes]
            print(f"   Routes found: {routes}")
            
            if "/context/{user_id}" in str(routes):
                print("✅ Context route registered in memory router")
            else:
                print("❌ Context route NOT registered in memory router")
                
        except Exception as e:
            print(f"❌ Failed to import memory router: {e}")
            
    except Exception as e:
        print(f"❌ Failed to check FastAPI routes: {e}")

def suggest_fixes():
    """Suggest fixes based on findings"""
    print("\n🔧 SUGGESTED FIXES:")
    print("=" * 40)
    
    print("1. Check the last few lines of your endpoint files:")
    print("   tail -20 backend/app/endpoints/modules.py")
    print("   tail -20 backend/app/endpoints/memory.py")
    print()
    
    print("2. Look for syntax errors or missing imports")
    print()
    
    print("3. If endpoints are malformed, run:")
    print("   python clean_and_readd_endpoints.py")
    print()
    
    print("4. Check backend logs for import errors when starting")

def main():
    """Main diagnosis function"""
    print("🔍 DIAGNOSING ENDPOINT ISSUES")
    print("=" * 40)
    
    check_file_syntax()
    check_endpoint_content()
    check_fastapi_routes()
    suggest_fixes()
    
    print("\n" + "=" * 40)
    print("🎯 DIAGNOSIS COMPLETE")
    print("=" * 40)

if __name__ == "__main__":
    main()
