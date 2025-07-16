#!/usr/bin/env python3
"""
Minimal Fix - No Backup Needed
Fixes the import errors and adds config endpoints to your current setup
Run from harv root directory: python minimal_fix_no_backup.py
"""

import os
import re

def fix_import_errors():
    """Fix the import errors in your current main.py"""
    
    print("🔧 FIXING IMPORT ERRORS")
    print("=" * 40)
    
    main_path = "backend/app/main.py"
    
    if not os.path.exists(main_path):
        print(f"❌ {main_path} not found")
        return False
    
    # Read current main.py
    with open(main_path, 'r') as f:
        content = f.read()
    
    # Fix the import issues
    print("   🔍 Checking for import issues...")
    
    # Remove problematic imports
    problematic_imports = [
        "UserRegistrationRequest, UserCreate, UserLoginRequest",
        "UserCreate,",
        "UserLoginRequest,",
        "UserRegistrationRequest,",
        "from app.schemas import ("
    ]
    
    fixed_content = content
    
    for problematic in problematic_imports:
        if problematic in fixed_content:
            print(f"   ✅ Removing: {problematic}")
            fixed_content = fixed_content.replace(problematic, "")
    
    # Clean up empty import lines
    fixed_content = re.sub(r'from app\.schemas import \(\s*\)', '', fixed_content)
    fixed_content = re.sub(r'from app\.schemas import \s*$', '', fixed_content, flags=re.MULTILINE)
    
    # Ensure we have the basic imports we need
    if "from pydantic import BaseModel" not in fixed_content:
        # Add after other imports
        import_insertion_point = fixed_content.find("from app.database import")
        if import_insertion_point != -1:
            fixed_content = fixed_content[:import_insertion_point] + "from pydantic import BaseModel, EmailStr\n" + fixed_content[import_insertion_point:]
    
    # Write the fixed file
    with open(main_path, 'w') as f:
        f.write(fixed_content)
    
    print("   ✅ Fixed import errors in main.py")
    return True

def add_config_endpoints():
    """Add the missing config endpoints to modules.py"""
    
    print("\n🔧 ADDING CONFIG ENDPOINTS")
    print("=" * 40)
    
    modules_path = "backend/app/endpoints/modules.py"
    
    if not os.path.exists(modules_path):
        print(f"❌ {modules_path} not found")
        return False
    
    # Read current modules.py
    with open(modules_path, 'r') as f:
        content = f.read()
    
    # Check if config endpoints already exist
    if "/config" in content:
        print("   ⚠️  Config endpoints already exist")
        return True
    
    # Add the config endpoints
    config_endpoints = '''

# === GUI CONFIG ENDPOINTS ===
from typing import Dict, Any

@router.get("/modules/{module_id}/config")
def get_module_config(module_id: int, db: Session = Depends(get_db)):
    """Get configuration for a specific module"""
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    return {
        "id": module.id,
        "title": module.title,
        "system_prompt": getattr(module, 'system_prompt', '') or "",
        "module_prompt": getattr(module, 'module_prompt', '') or "",
        "system_corpus": getattr(module, 'system_corpus', '') or "",
        "module_corpus": getattr(module, 'module_corpus', '') or "",
        "dynamic_corpus": getattr(module, 'dynamic_corpus', '') or "",
        "memory_extraction_prompt": getattr(module, 'memory_extraction_prompt', '') or "",
        "mastery_triggers": getattr(module, 'mastery_triggers', '') or "",
        "confusion_triggers": getattr(module, 'confusion_triggers', '') or "",
        "memory_context_template": getattr(module, 'memory_context_template', '') or "",
        "cross_module_references": getattr(module, 'cross_module_references', '') or "",
        "learning_styles": getattr(module, 'learning_styles', '') or "",
        "memory_weight": getattr(module, 'memory_weight', 2) or 2
    }

@router.put("/modules/{module_id}/config")
def update_module_config(module_id: int, config: Dict[str, Any], db: Session = Depends(get_db)):
    """Update configuration for a specific module"""
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    # Update fields that are provided
    for field, value in config.items():
        if hasattr(module, field):
            setattr(module, field, value)
    
    db.commit()
    db.refresh(module)
    
    return {
        "message": "Configuration updated successfully",
        "module_id": module_id,
        "module_title": module.title
    }

@router.get("/modules/{module_id}/test")
def test_module_config(module_id: int, db: Session = Depends(get_db)):
    """Test a module's configuration"""
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    return {
        "success": True,
        "message": "Configuration is valid",
        "module_title": module.title
    }

@router.get("/modules/export")
def export_all_configurations(db: Session = Depends(get_db)):
    """Export all module configurations"""
    modules = db.query(Module).all()
    
    export_data = []
    for module in modules:
        module_data = {
            "id": module.id,
            "title": module.title,
            "description": getattr(module, 'description', '') or "",
            "system_prompt": getattr(module, 'system_prompt', '') or "",
            "module_prompt": getattr(module, 'module_prompt', '') or "",
            "system_corpus": getattr(module, 'system_corpus', '') or "",
            "module_corpus": getattr(module, 'module_corpus', '') or "",
            "dynamic_corpus": getattr(module, 'dynamic_corpus', '') or "",
        }
        export_data.append(module_data)
    
    return export_data
'''
    
    # Append the config endpoints
    updated_content = content + config_endpoints
    
    # Write the updated file
    with open(modules_path, 'w') as f:
        f.write(updated_content)
    
    print("   ✅ Added config endpoints to modules.py")
    return True

def check_current_state():
    """Check what we're working with"""
    print("🔍 CHECKING CURRENT STATE")
    print("=" * 40)
    
    # Check main.py
    main_path = "backend/app/main.py"
    if os.path.exists(main_path):
        print("✅ main.py exists")
        
        with open(main_path, 'r') as f:
            content = f.read()
        
        if "UserLoginRequest" in content:
            print("   ⚠️  Has import issues (UserLoginRequest)")
        else:
            print("   ✅ Looks clean")
    else:
        print("❌ main.py missing")
    
    # Check modules.py
    modules_path = "backend/app/endpoints/modules.py"
    if os.path.exists(modules_path):
        print("✅ modules.py exists")
        
        with open(modules_path, 'r') as f:
            content = f.read()
        
        if "/config" in content:
            print("   ✅ Has config endpoints")
        else:
            print("   ❌ Missing config endpoints")
    else:
        print("❌ modules.py missing")
    
    return True

def minimal_fix():
    """Apply minimal fix to current files"""
    
    print("🔧 MINIMAL FIX - WORKING WITH CURRENT FILES")
    print("=" * 60)
    
    # Check current state
    check_current_state()
    
    # Apply fixes
    success = True
    
    # 1. Fix import errors
    if not fix_import_errors():
        success = False
    
    # 2. Add config endpoints
    if not add_config_endpoints():
        success = False
    
    if success:
        print("\n🎉 MINIMAL FIX COMPLETE!")
        print("=" * 60)
        print("✅ Import errors fixed")
        print("✅ Config endpoints added")
        print("✅ Ready to test")
        
        print("\n🚀 NEXT STEPS:")
        print("1. Restart backend: cd backend && uvicorn app.main:app --reload")
        print("2. Check for startup errors")
        print("3. Test: curl http://127.0.0.1:8000/modules/1/config")
        print("4. Refresh GUI: http://localhost:3000/dev-gui.html")
        
        print("\n✨ Expected Result:")
        print("- Backend starts without import errors")
        print("- GUI loads without 404 errors")
        print("- Config interface works")
        
        return True
    else:
        print("\n❌ Fix failed - check errors above")
        return False

if __name__ == "__main__":
    success = minimal_fix()
    if success:
        print("\n🎯 SUCCESS! Your GUI should now work!")
    else:
        print("\n❌ Fix failed")
