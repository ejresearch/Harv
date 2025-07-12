"""
FIXED FastAPI Main Application - Simple Copy-Paste Solution
Replace your entire backend/app/main.py with this file
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import os
import json

# FIXED IMPORTS - Using only auth.py (removed auth_working conflicts)
from app.database import get_db, engine
from app.models import Base, Module, User, Conversation, MemorySummary
from app.auth import (
    authenticate_user, create_user_tokens, get_password_hash,
    create_user_account, get_current_user
)

# Import endpoints
from app.endpoints.modules import router as modules_router
from app.endpoints.chat import router as chat_router
from app.endpoints.memory import router as memory_router

# Create FastAPI app
app = FastAPI(
    title="Harv Backend - FIXED VERSION",
    description="GUI-to-Frontend integrated system",
    version="2.0.0"
)

# FIXED CORS - More restrictive
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(modules_router)
app.include_router(chat_router)
app.include_router(memory_router)

# Create tables on startup
@app.on_event("startup")
def startup_event():
    print("🚀 Starting FIXED Harv Backend...")
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
        "Introduction to Mass Communication", "History and Evolution of Media", 
        "Media Theory and Effects", "Print Media and Journalism",
        "Broadcasting: Radio and Television", "Digital Media and the Internet",
        "Social Media and New Platforms", "Media Ethics and Responsibility",
        "Media Law and Regulation", "Advertising and Public Relations",
        "Media Economics and Business Models", "Global Media and Cultural Impact",
        "Media Literacy and Critical Analysis", "Future of Mass Communication",
        "Capstone: Integrating Knowledge"
    ]
    
    for i, title in enumerate(modules, 1):
        module = Module(
            id=i, title=title, description=f"Module {i} of the Mass Communication course",
            resources="", system_prompt="", module_prompt="", system_corpus="",
            module_corpus="", dynamic_corpus="",
            api_endpoint="https://api.openai.com/v1/chat/completions"
        )
        db.add(module)
    
    db.commit()
    print(f"✅ Auto-populated {len(modules)} modules")

# Health check
@app.get("/")
def root():
    return {
        "message": "🎉 Harv Backend - FIXED VERSION",
        "status": "running",
        "gui_integration": "enabled",
        "frontend_ready": True
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "2.0.0"}

# FIXED AUTH ENDPOINTS
from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    reason: str = ""
    familiarity: str = ""
    learning_style: str = ""
    goals: str = ""
    background: str = ""

@app.post("/auth/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """FIXED login endpoint"""
    try:
        user = authenticate_user(db, request.email, request.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        tokens = create_user_tokens(user.id)
        
        return {
            "success": True,
            "user_id": user.id,
            "user": {"id": user.id, "email": user.email, "name": user.name},
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": tokens["token_type"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Login failed")

@app.post("/auth/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """FIXED registration endpoint"""
    try:
        user = create_user_account(
            db=db, email=request.email, password=request.password, name=request.name,
            reason=request.reason, familiarity=request.familiarity,
            learning_style=request.learning_style, goals=request.goals,
            background=request.background
        )
        
        tokens = create_user_tokens(user.id)
        
        return {
            "success": True,
            "user_id": user.id,
            "user": {"id": user.id, "email": user.email, "name": user.name},
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": tokens["token_type"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Registration failed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
