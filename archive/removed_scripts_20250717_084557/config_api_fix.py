#!/usr/bin/env python3
"""
Module Configuration API Fix
Adds the missing config endpoints to your existing modules.py file
Run from harv root directory: python config_api_fix.py
"""

import os
import shutil
from datetime import datetime

def add_config_endpoints():
    """Add the missing config endpoints to your existing modules.py"""
    
    print("🔧 Adding Configuration API Endpoints")
    print("=" * 50)
    
    # Check if modules.py exists
    modules_path = "backend/app/endpoints/modules.py"
    if not os.path.exists(modules_path):
        print(f"❌ {modules_path} not found")
        return
    
    # Create backup
    backup_path = f"backend/app/endpoints/modules.py.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(modules_path, backup_path)
    print(f"📁 Backup created: {backup_path}")
    
    # Read current content
    with open(modules_path, 'r') as f:
        content = f.read()
    
    # Check if endpoints already exist
    if "/config" in content:
        print("✅ Config endpoints already exist")
        return
    
    # Add the missing config endpoints
    config_endpoints = '''

# Configuration endpoints for GUI
@router.get("/{module_id}/config")
def get_module_config(module_id: int, db: Session = Depends(get_db)):
    """Get configuration for a specific module"""
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    return {
        "id": module.id,
        "title": getattr(module, 'title', f'Module {module.id}'),
        "system_prompt": getattr(module, 'system_prompt', ''),
        "module_prompt": getattr(module, 'module_prompt', ''),
        "system_corpus": getattr(module, 'system_corpus', ''),
        "module_corpus": getattr(module, 'module_corpus', ''),
        "dynamic_corpus": getattr(module, 'dynamic_corpus', ''),
        "memory_extraction_prompt": getattr(module, 'memory_extraction_prompt', ''),
        "mastery_triggers": getattr(module, 'mastery_triggers', ''),
        "confusion_triggers": getattr(module, 'confusion_triggers', ''),
        "memory_context_template": getattr(module, 'memory_context_template', ''),
        "cross_module_references": getattr(module, 'cross_module_references', ''),
        "learning_styles": getattr(module, 'learning_styles', ''),
        "memory_weight": getattr(module, 'memory_weight', 2)
    }

@router.put("/{module_id}/config")
def update_module_config(module_id: int, config: dict, db: Session = Depends(get_db)):
    """Update configuration for a specific module"""
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    # Update fields safely
    updatable_fields = [
        'system_prompt', 'module_prompt', 'system_corpus', 'module_corpus',
        'dynamic_corpus', 'memory_extraction_prompt', 'mastery_triggers',
        'confusion_triggers', 'memory_context_template', 'cross_module_references',
        'learning_styles', 'memory_weight'
    ]
    
    for field, value in config.items():
        if field in updatable_fields and hasattr(module, field):
            setattr(module, field, value)
    
    db.commit()
    return {"message": "Configuration updated successfully"}

@router.get("/{module_id}/test")
def test_module_config(module_id: int, db: Session = Depends(get_db)):
    """Test configuration for a specific module"""
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    return {
        "status": "success",
        "module": module.title or f"Module {module.id}",
        "has_prompts": bool(getattr(module, 'system_prompt', '')),
        "memory_ready": bool(getattr(module, 'memory_extraction_prompt', ''))
    }

@router.get("/export")
def export_all_configs(db: Session = Depends(get_db)):
    """Export all module configurations"""
    modules = db.query(Module).all()
    
    export_data = []
    for module in modules:
        export_data.append({
            "id": module.id,
            "title": getattr(module, 'title', f'Module {module.id}'),
            "system_prompt": getattr(module, 'system_prompt', ''),
            "module_prompt": getattr(module, 'module_prompt', ''),
            "memory_extraction_prompt": getattr(module, 'memory_extraction_prompt', ''),
            "mastery_triggers": getattr(module, 'mastery_triggers', ''),
            "confusion_triggers": getattr(module, 'confusion_triggers', '')
        })
    
    return {"modules": export_data}
'''
    
    # Append the endpoints to the file
    with open(modules_path, 'a') as f:
        f.write(config_endpoints)
    
    print("✅ Config endpoints added successfully")
    print("")
    print("🚀 Next Steps:")
    print("1. cd backend")
    print("2. uvicorn app.main:app --reload")
    print("3. Test: curl http://127.0.0.1:8000/modules/1/config")
    print("4. Open GUI: http://localhost:3000/dev-gui.html")
    print("")
    print("🎯 Your GUI should now work without 404 errors!")

if __name__ == "__main__":
    add_config_endpoints()
