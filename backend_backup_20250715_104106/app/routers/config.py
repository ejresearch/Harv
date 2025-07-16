from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Module
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class ModuleConfigRequest(BaseModel):
    system_prompt: Optional[str] = None
    module_prompt: Optional[str] = None
    course_knowledge_base: Optional[str] = None
    module_resources: Optional[str] = None
    current_events: Optional[str] = None
    memory_extraction_prompt: Optional[str] = None
    mastery_triggers: Optional[str] = None
    confusion_triggers: Optional[str] = None
    memory_context_template: Optional[str] = None
    cross_module_references: Optional[str] = None

class ModuleConfigResponse(BaseModel):
    id: int
    name: str
    system_prompt: Optional[str] = None
    module_prompt: Optional[str] = None
    course_knowledge_base: Optional[str] = None
    module_resources: Optional[str] = None
    current_events: Optional[str] = None
    memory_extraction_prompt: Optional[str] = None
    mastery_triggers: Optional[str] = None
    confusion_triggers: Optional[str] = None
    memory_context_template: Optional[str] = None
    cross_module_references: Optional[str] = None

@router.get("/modules/{module_id}/config", response_model=ModuleConfigResponse)
async def get_module_config(module_id: int, db: Session = Depends(get_db)):
    """Get configuration for a specific module"""
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    return ModuleConfigResponse(
        id=module.id,
        name=module.name,
        system_prompt=module.system_prompt,
        module_prompt=module.module_prompt,
        course_knowledge_base=module.course_knowledge_base,
        module_resources=module.module_resources,
        current_events=module.current_events,
        memory_extraction_prompt=module.memory_extraction_prompt,
        mastery_triggers=module.mastery_triggers,
        confusion_triggers=module.confusion_triggers,
        memory_context_template=module.memory_context_template,
        cross_module_references=module.cross_module_references
    )

@router.put("/modules/{module_id}/config")
async def update_module_config(
    module_id: int, 
    config: ModuleConfigRequest,
    db: Session = Depends(get_db)
):
    """Update configuration for a specific module"""
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    # Update only provided fields
    update_data = config.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(module, field, value)
    
    try:
        db.commit()
        db.refresh(module)
        return {"message": "Configuration updated successfully", "module_id": module_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update configuration: {str(e)}")

@router.get("/modules", response_model=list[ModuleConfigResponse])
async def get_all_modules(db: Session = Depends(get_db)):
    """Get all modules with their configurations"""
    modules = db.query(Module).all()
    return [
        ModuleConfigResponse(
            id=module.id,
            name=module.name,
            system_prompt=module.system_prompt,
            module_prompt=module.module_prompt,
            course_knowledge_base=module.course_knowledge_base,
            module_resources=module.module_resources,
            current_events=module.current_events,
            memory_extraction_prompt=module.memory_extraction_prompt,
            mastery_triggers=module.mastery_triggers,
            confusion_triggers=module.confusion_triggers,
            memory_context_template=module.memory_context_template,
            cross_module_references=module.cross_module_references
        ) for module in modules
    ]
