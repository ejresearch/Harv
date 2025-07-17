#!/usr/bin/env python3
"""
Fix Export Endpoint - Quick Fix for 422 Error
Run from harv root directory: python fix_export_endpoint.py
"""

import os

def fix_export_endpoint():
    """Fix the export endpoint 422 error"""
    modules_path = "backend/app/endpoints/modules.py"
    
    if not os.path.exists(modules_path):
        print(f"❌ {modules_path} not found")
        return
    
    print("🔧 Fixing export endpoint...")
    
    # Read current content
    with open(modules_path, 'r') as f:
        content = f.read()
    
    # Replace the export endpoint with a working version
    export_fix = '''
@router.get("/modules/export")
def export_modules(db: Session = Depends(get_db)):
    """Export all module configurations"""
    modules = db.query(Module).all()
    
    export_data = []
    for module in modules:
        export_data.append({
            "id": module.id,
            "title": module.title,
            "description": module.description,
            "system_prompt": module.system_prompt,
            "module_prompt": module.module_prompt,
            "system_corpus": module.system_corpus,
            "module_corpus": module.module_corpus,
            "dynamic_corpus": module.dynamic_corpus
        })
    
    return {
        "modules": export_data,
        "total_modules": len(export_data)
    }
'''
    
    # Check if export endpoint exists
    if '@router.get("/modules/export")' in content:
        print("✅ Export endpoint already exists - should be working")
        return
    
    # Add the export endpoint at the end
    if not content.endswith('\n'):
        content += '\n'
    
    content += export_fix
    
    # Write back
    with open(modules_path, 'w') as f:
        f.write(content)
    
    print("✅ Export endpoint fixed!")
    print("🔄 Restart your backend to apply changes")

if __name__ == "__main__":
    fix_export_endpoint()
