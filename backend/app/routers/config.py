"""
Module configuration API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from ..database import get_db
from ..models import Module
from pydantic import BaseModel

router = APIRouter(prefix="/modules", tags=["modules"])

class ModuleConfigUpdate(BaseModel):
    module_prompt: str = None
    system_corpus: str = None
    module_corpus: str = None
    dynamic_corpus: str = None
    memory_extraction_prompt: str = None
    mastery_triggers: str = None
    confusion_triggers: str = None
    memory_context_template: str = None
    cross_module_references: str = None
    learning_styles: str = None
    memory_weight: int = 2

@router.get("/{module_id}/config")
async def get_module_config(module_id: int, db: Session = Depends(get_db)):
    """Get configuration for a specific module"""
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    return {
        "id": module.id,
        "title": module.title,
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
async def update_module_config(
    module_id: int, 
    config: ModuleConfigUpdate, 
    db: Session = Depends(get_db)
):
    """Update configuration for a specific module"""
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    # Update fields that are provided
    for field, value in config.dict(exclude_unset=True).items():
        if hasattr(module, field):
            setattr(module, field, value)
    
    db.commit()
    db.refresh(module)
    
    return {"message": "Configuration updated successfully", "module_id": module_id}

@router.get("/{module_id}/test")
async def test_module_config(module_id: int, db: Session = Depends(get_db)):
    """Test a module's configuration"""
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    # Basic validation
    required_fields = ['module_prompt', 'system_corpus']
    missing_fields = []
    
    for field in required_fields:
        if not getattr(module, field, None):
            missing_fields.append(field)
    
    if missing_fields:
        return {
            "success": False,
            "error": f"Missing required fields: {', '.join(missing_fields)}"
        }
    
    return {
        "success": True,
        "message": "Configuration is valid",
        "module_title": module.title
    }

@router.get("/export")
async def export_all_configurations(db: Session = Depends(get_db)):
    """Export all module configurations"""
    modules = db.query(Module).all()
    
    export_data = []
    for module in modules:
        module_data = {
            "id": module.id,
            "title": module.title,
            "description": module.description,
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
        export_data.append(module_data)
    
    from fastapi.responses import JSONResponse
    import json
    
    return JSONResponse(
        content=export_data,
        headers={"Content-Disposition": "attachment; filename=harv_module_configurations.json"}
    )
