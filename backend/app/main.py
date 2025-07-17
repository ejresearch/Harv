"""
Complete FastAPI Main Application with Memory System Integration
Replace your entire backend/app/main.py with this file
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import os
import json

# Import database and models
from app.database import get_db, engine
from app.models import Base, Module, User, Conversation, MemorySummary

# Import authentication
from app.auth import (
    authenticate_user, create_user_tokens, get_password_hash,
    create_user_account, get_current_user
)

# Import all endpoint routers
from app.endpoints.modules import router as modules_router
try:
    from app.endpoints.chat import router as chat_router
except ImportError:
    from app.routers.chat import router as chat_router
from app.endpoints.memory import router as memory_router
from app.endpoints.conversations import router as conversations_router
try:
    from app.endpoints.auth import router as auth_router
except ImportError:
    from app.routers.auth import router as auth_router

# Create FastAPI app
app = FastAPI(
    title="Harv Backend - Memory-Aware System",
    description="AI Tutoring Platform with 4-Layer Memory System",
    version="3.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000", 
        "http://localhost:3001",  # Demo frontend
        "http://127.0.0.1:3001",  # Demo frontend
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(modules_router)
app.include_router(chat_router, prefix="/chat")
app.include_router(memory_router)
app.include_router(conversations_router, prefix="/conversations")  # Memory router already has its own prefix
app.include_router(auth_router)    # Auth router already has its own prefix

# Create tables on startup
@app.on_event("startup")
def startup_event():
    print("🚀 Starting Harv Backend with Memory System...")
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
            system_prompt="You are Harv, a Socratic tutor for mass communication. Guide students through thoughtful questions rather than giving direct answers.",
            module_prompt="Focus on helping students discover concepts through questioning.", 
            system_corpus="Core concepts: media theory, communication effects, journalism ethics, digital transformation",
            module_corpus="", 
            dynamic_corpus="",
            api_endpoint="https://api.openai.com/v1/chat/completions"
        )
        db.add(module)
    
    db.commit()
    print(f"✅ Auto-populated {len(modules)} modules")

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "🎉 Harv Backend - Memory-Aware AI Tutoring System",
        "status": "running",
        "version": "3.0.0",
        "features": [
            "4-layer memory system",
            "Socratic tutoring",
            "15 mass communication modules",
            "Export-triggered memory extraction",
            "Memory-enhanced responses"
        ]
    }

# Health check
@app.get("/health")
def health_check():
    """Enhanced health check with system status"""
    db = next(get_db())
    try:
        # Check database connectivity
        module_count = db.query(Module).count()
        user_count = db.query(User).count()
        conversation_count = db.query(Conversation).count()
        memory_count = db.query(MemorySummary).count()
        
        # Check OpenAI API key
        has_openai_key = bool(os.getenv("OPENAI_API_KEY"))
        
        return {
            "status": "healthy",
            "version": "3.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "database": {
                "modules": module_count,
                "users": user_count,
                "conversations": conversation_count,
                "memory_summaries": memory_count
            },
            "openai_configured": has_openai_key,
            "memory_system": "active"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
    finally:
        db.close()

# Simplified auth endpoints for backward compatibility
from pydantic import BaseModel, EmailStr

class SimpleLoginRequest(BaseModel):
    email: EmailStr
    password: str

class SimpleRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    reason: str = ""
    familiarity: str = ""
    learning_style: str = ""
    goals: str = ""
    background: str = ""

@app.post("/auth/login")
def simple_login(request: SimpleLoginRequest, db: Session = Depends(get_db)):
    """Simplified login endpoint for frontend compatibility"""
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
        print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.post("/auth/register")
def simple_register(request: SimpleRegisterRequest, db: Session = Depends(get_db)):
    """Simplified registration endpoint for frontend compatibility"""
    try:
        user = create_user_account(
            db=db, 
            email=request.email, 
            password=request.password, 
            name=request.name,
            reason=request.reason, 
            familiarity=request.familiarity,
            learning_style=request.learning_style, 
            goals=request.goals,
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
        print(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
