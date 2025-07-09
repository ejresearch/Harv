from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models import Module
from app.database import get_db
from typing import Optional

router = APIRouter()

class ModuleConfig(BaseModel):
    system_prompt: Optional[str] = None
    module_prompt: Optional[str] = None
    system_corpus: Optional[str] = None
    module_corpus: Optional[str] = None
    dynamic_corpus: Optional[str] = None
    api_endpoint: Optional[str] = None

class ModuleOut(BaseModel):
    id: int
    title: str
    description: str
    resources: str
    system_prompt: Optional[str] = None
    module_prompt: Optional[str] = None
    system_corpus: Optional[str] = None
    module_corpus: Optional[str] = None
    dynamic_corpus: Optional[str] = None
    api_endpoint: Optional[str] = None
    
    class Config:
        from_attributes = True

@router.get("/modules", response_model=list[ModuleOut])
def get_modules(db: Session = Depends(get_db)):
    modules = db.query(Module).all()
    return modules

@router.get("/modules/{module_id}", response_model=ModuleOut)
def get_module_config(module_id: int, db: Session = Depends(get_db)):
    """Get GPT configuration for a specific module"""
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    return module

@router.put("/modules/{module_id}")
def update_module_config(module_id: int, config: ModuleConfig, db: Session = Depends(get_db)):
    """Save/update GPT configuration for a specific module"""
    module = db.query(Module).filter(Module.id == module_id).first()
    
    if not module:
        # Create new module if it doesn't exist
        module = Module(
            id=module_id, 
            title=f"Module {module_id}",
            description="",
            resources=""
        )
        db.add(module)
    
    # Update configuration fields
    if config.system_prompt is not None:
        module.system_prompt = config.system_prompt
    if config.module_prompt is not None:
        module.module_prompt = config.module_prompt
    if config.system_corpus is not None:
        module.system_corpus = config.system_corpus
    if config.module_corpus is not None:
        module.module_corpus = config.module_corpus
    if config.dynamic_corpus is not None:
        module.dynamic_corpus = config.dynamic_corpus
    if config.api_endpoint is not None:
        module.api_endpoint = config.api_endpoint
    
    db.commit()
    db.refresh(module)
    return {"message": f"Configuration saved for Module {module_id}", "module_id": module_id}

@router.post("/modules/populate")
def populate_module_titles(db: Session = Depends(get_db)):
    """Helper endpoint to populate the 15 Mass Communication modules"""
    mass_comm_modules = [
        "Introduction to Mass Communication",
        "History and Evolution of Media", 
        "Media Theory and Effects",
        "Print Media and Journalism",
        "Broadcasting: Radio and Television",
        "Digital Media and the Internet",
        "Social Media and New Platforms",
        "Media Ethics and Responsibility",
        "Media Law and Regulation",
        "Advertising and Public Relations",
        "Media Economics and Business Models",
        "Global Media and Cultural Impact",
        "Media Literacy and Critical Analysis",
        "Future of Mass Communication",
        "Capstone: Integrating Knowledge"
    ]
    
    created_modules = []
    for i, title in enumerate(mass_comm_modules, 1):
        existing = db.query(Module).filter(Module.id == i).first()
        if not existing:
            module = Module(
                id=i,
                title=title,
                description=f"Module {i} of the Mass Communication course",
                resources="",
                system_prompt="",
                module_prompt="",
                system_corpus="",
                module_corpus="",
                dynamic_corpus=""
            )
            db.add(module)
            created_modules.append(i)
    
    db.commit()
    return {"message": f"Created {len(created_modules)} modules", "modules": created_modules}
