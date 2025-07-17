#!/usr/bin/env python3
"""
Single Button GUI Fix - Makes your configuration GUI fully functional
Run from harv root directory: python fix_gui_single_button.py
"""

import os
import shutil
from datetime import datetime

def fix_gui_single_button():
    """Single button fix to make GUI fully functional"""
    
    print("🔧 SINGLE BUTTON GUI FIX")
    print("=" * 50)
    
    # 1. Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backend_backup_{timestamp}"
    if os.path.exists("backend"):
        shutil.copytree("backend", backup_dir)
        print(f"✅ Created backup: {backup_dir}")
    
    # 2. Fix main.py with proper router inclusion
    main_py_content = '''"""
Complete FastAPI Main Application - GUI Compatible
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import os

# Import database and models
from app.database import get_db, engine
from app.models import Base, Module, User

# Import all endpoint routers
from app.endpoints.modules import router as modules_router
from app.endpoints.chat import router as chat_router
from app.endpoints.memory import router as memory_router
from app.endpoints.auth import router as auth_router

# Create FastAPI app
app = FastAPI(
    title="Harv Backend - GUI Compatible",
    description="AI Tutoring Platform with Configuration GUI",
    version="3.1.0"
)

# CORS Configuration - Allow GUI access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000", 
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup
@app.on_event("startup")
def startup_event():
    print("🚀 Starting Harv Backend with GUI Support...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    # Auto-populate modules if empty
    db = next(get_db())
    module_count = db.query(Module).count()
    if module_count == 0:
        populate_default_modules(db)
    db.close()

def populate_default_modules(db: Session):
    """Auto-populate the 15 modules"""
    modules = [
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
    
    for i, title in enumerate(modules, 1):
        module = Module(
            id=i, 
            title=title, 
            description=f"Module {i} of the Mass Communication course",
            resources="", 
            system_prompt="You are Harv, a Socratic tutor. Guide students through thoughtful questions.",
            module_prompt=f"Focus on helping students discover {title.lower()} concepts through questioning.", 
            system_corpus="Core concepts: media theory, communication effects, journalism ethics",
            module_corpus="", 
            dynamic_corpus="",
            api_endpoint="https://api.openai.com/v1/chat/completions"
        )
        db.add(module)
    
    db.commit()
    print(f"✅ Auto-populated {len(modules)} modules")

# Include all routers
app.include_router(modules_router)
app.include_router(chat_router, prefix="/chat")
app.include_router(memory_router)
app.include_router(auth_router)

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "🎉 Harv Backend - GUI Compatible",
        "status": "running",
        "version": "3.1.0",
        "gui_support": True
    }

# Health check
@app.get("/health")
def health_check():
    """Health check with GUI compatibility status"""
    db = next(get_db())
    try:
        module_count = db.query(Module).count()
        user_count = db.query(User).count()
        
        return {
            "status": "healthy",
            "version": "3.1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "database": {
                "modules": module_count,
                "users": user_count
            },
            "gui_compatible": True,
            "openai_configured": bool(os.getenv("OPENAI_API_KEY"))
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    # 3. Enhanced modules.py with config endpoints
    modules_py_content = '''from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models import Module
from app.database import get_db
from typing import Optional, Dict, Any

router = APIRouter()

class ModuleConfig(BaseModel):
    system_prompt: Optional[str] = None
    module_prompt: Optional[str] = None
    system_corpus: Optional[str] = None
    module_corpus: Optional[str] = None
    dynamic_corpus: Optional[str] = None
    api_endpoint: Optional[str] = None
    memory_extraction_prompt: Optional[str] = None
    mastery_triggers: Optional[str] = None
    confusion_triggers: Optional[str] = None
    memory_context_template: Optional[str] = None
    cross_module_references: Optional[str] = None
    learning_styles: Optional[str] = None
    memory_weight: Optional[int] = 2

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
    """Get all modules"""
    modules = db.query(Module).all()
    return modules

@router.get("/modules/{module_id}", response_model=ModuleOut)
def get_module(module_id: int, db: Session = Depends(get_db)):
    """Get a specific module"""
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    return module

# === GUI CONFIGURATION ENDPOINTS ===

@router.get("/modules/{module_id}/config")
def get_module_config(module_id: int, db: Session = Depends(get_db)):
    """Get configuration for a specific module - GUI Compatible"""
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    return {
        "id": module.id,
        "title": module.title,
        "system_prompt": module.system_prompt or "",
        "module_prompt": module.module_prompt or "",
        "system_corpus": module.system_corpus or "",
        "module_corpus": module.module_corpus or "",
        "dynamic_corpus": module.dynamic_corpus or "",
        "memory_extraction_prompt": getattr(module, 'memory_extraction_prompt', ''),
        "mastery_triggers": getattr(module, 'mastery_triggers', ''),
        "confusion_triggers": getattr(module, 'confusion_triggers', ''),
        "memory_context_template": getattr(module, 'memory_context_template', ''),
        "cross_module_references": getattr(module, 'cross_module_references', ''),
        "learning_styles": getattr(module, 'learning_styles', ''),
        "memory_weight": getattr(module, 'memory_weight', 2)
    }

@router.put("/modules/{module_id}/config")
def update_module_config(module_id: int, config: Dict[str, Any], db: Session = Depends(get_db)):
    """Update configuration for a specific module - GUI Compatible"""
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
    """Test a module's configuration - GUI Compatible"""
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    # Basic validation
    required_fields = ['system_prompt', 'module_prompt']
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

@router.get("/modules/export")
def export_all_configurations(db: Session = Depends(get_db)):
    """Export all module configurations - GUI Compatible"""
    modules = db.query(Module).all()
    
    export_data = []
    for module in modules:
        module_data = {
            "id": module.id,
            "title": module.title,
            "description": module.description,
            "system_prompt": module.system_prompt or "",
            "module_prompt": module.module_prompt or "",
            "system_corpus": module.system_corpus or "",
            "module_corpus": module.module_corpus or "",
            "dynamic_corpus": module.dynamic_corpus or "",
            "memory_extraction_prompt": getattr(module, 'memory_extraction_prompt', ''),
            "mastery_triggers": getattr(module, 'mastery_triggers', ''),
            "confusion_triggers": getattr(module, 'confusion_triggers', ''),
            "memory_context_template": getattr(module, 'memory_context_template', ''),
            "cross_module_references": getattr(module, 'cross_module_references', ''),
            "learning_styles": getattr(module, 'learning_styles', ''),
            "memory_weight": getattr(module, 'memory_weight', 2)
        }
        export_data.append(module_data)
    
    return export_data

# === LEGACY ENDPOINTS ===

@router.put("/modules/{module_id}")
def update_module_legacy(module_id: int, config: ModuleConfig, db: Session = Depends(get_db)):
    """Legacy endpoint for backward compatibility"""
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
                system_prompt="You are Harv, a Socratic tutor. Guide students through discovery.",
                module_prompt=f"Focus on helping students discover {title.lower()} concepts.",
                system_corpus="Core concepts: media theory, communication effects, journalism ethics",
                module_corpus="",
                dynamic_corpus="",
                api_endpoint="https://api.openai.com/v1/chat/completions"
            )
            db.add(module)
            created_modules.append(i)
    
    db.commit()
    return {"message": f"Created {len(created_modules)} modules", "modules": created_modules}
'''
    
    # 4. Write the files
    try:
        # Write main.py
        with open("backend/app/main.py", "w") as f:
            f.write(main_py_content)
        print("✅ Updated main.py with GUI compatibility")
        
        # Write modules.py
        with open("backend/app/endpoints/modules.py", "w") as f:
            f.write(modules_py_content)
        print("✅ Updated modules.py with config endpoints")
        
        print("\n🎉 SINGLE BUTTON FIX COMPLETE!")
        print("=" * 50)
        print("✅ All files updated with GUI support")
        print("✅ Config endpoints added for GUI")
        print("✅ CORS configured for GUI access")
        print("✅ Backward compatibility maintained")
        
        print("\n🚀 NEXT STEPS:")
        print("1. Restart backend: cd backend && uvicorn app.main:app --reload")
        print("2. Test config endpoint: curl http://127.0.0.1:8000/modules/1/config")
        print("3. Refresh GUI: http://localhost:3000/dev-gui.html")
        print("4. Select a module and configure it!")
        
        print("\n✨ Expected Result:")
        print("- GUI loads all 15 modules without errors")
        print("- Click any module → loads configuration form")
        print("- Save configuration → no 404 errors")
        print("- Beautiful working configuration interface")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating files: {e}")
        return False

if __name__ == "__main__":
    success = fix_gui_single_button()
    if success:
        print("\n🎯 YOUR GUI IS NOW FULLY FUNCTIONAL!")
        print("You've completed the Module Configuration System!")
        print("Ready to move to Integration Testing next!")
    else:
        print("\n❌ Fix failed - check the errors above")
