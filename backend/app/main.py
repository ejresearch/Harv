"""
Complete FastAPI Main Application with Enhanced Memory System Integration
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

# Import chat router with fallback
try:
    from app.endpoints.chat import router as chat_router
    print("✅ Chat router loaded from endpoints")
except ImportError:
    try:
        from app.routers.chat import router as chat_router
        print("✅ Chat router loaded from routers")
    except ImportError:
        print("⚠️ Chat router not found, creating fallback")
        from fastapi import APIRouter
        chat_router = APIRouter()
        
        @chat_router.get("/health")
        def chat_health():
            return {"status": "Chat router fallback active"}

# Import other routers with fallbacks
try:
    from app.endpoints.memory import router as memory_router
    print("✅ Memory router loaded")
except ImportError:
    print("⚠️ Memory router not found, creating fallback")
    from fastapi import APIRouter
    memory_router = APIRouter()

try:
    from app.endpoints.conversations import router as conversations_router
    print("✅ Conversations router loaded")
except ImportError:
    print("⚠️ Conversations router not found, creating fallback")
    from fastapi import APIRouter
    conversations_router = APIRouter()

try:
    from app.endpoints.auth import router as auth_router
    print("✅ Auth router loaded from endpoints")
except ImportError:
    try:
        from app.routers.auth import router as auth_router
        print("✅ Auth router loaded from routers")
    except ImportError:
        print("⚠️ Auth router not found, will use inline auth")
        from fastapi import APIRouter
        auth_router = APIRouter()

# Check for enhanced memory system
try:
    from app.memory_context_enhanced import DynamicMemoryAssembler
    ENHANCED_MEMORY_AVAILABLE = True
    print("✅ Enhanced memory system loaded")
except ImportError:
    ENHANCED_MEMORY_AVAILABLE = False
    print("⚠️ Enhanced memory system not available")

# Create FastAPI app
app = FastAPI(
    title="Harv Backend - Enhanced Memory System",
    description="AI Tutoring Platform with 4-Layer Dynamic Memory System",
    version="4.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000", 
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers with proper prefixes
app.include_router(modules_router, prefix="", tags=["modules"])
app.include_router(chat_router, prefix="", tags=["chat"])  # No prefix so /chat/ works
app.include_router(memory_router, prefix="", tags=["memory"])
app.include_router(conversations_router, prefix="/conversations", tags=["conversations"])
app.include_router(auth_router, prefix="", tags=["auth"])

# Create tables on startup
@app.on_event("startup")
def startup_event():
    print("🚀 Starting Harv Backend with Enhanced Memory System...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    # Auto-populate modules if empty
    db = next(get_db())
    module_count = db.query(Module).count()
    if module_count == 0:
        populate_default_modules(db)
    db.close()
    
    print(f"🧠 Enhanced Memory System: {'Available' if ENHANCED_MEMORY_AVAILABLE else 'Not Available'}")

def populate_default_modules(db: Session):
    """Auto-populate the 15 Communication Media & Society modules"""
    modules = [
        {
            "id": 1,
            "title": "Your Four Worlds", 
            "description": "Communication models, perception, and the four worlds we live in",
            "system_prompt": "You are Harv, a Socratic tutor for communication theory. Guide students to discover the four worlds of communication through strategic questioning about perception, reality, and media influence.",
            "module_prompt": "Focus on helping students understand communication models, perception processes, and how media shapes our understanding of reality."
        },
        {
            "id": 2,
            "title": "Media Uses & Effects", 
            "description": "Functions vs effects, media theories, and societal impact",
            "system_prompt": "Guide students to discover the difference between media functions and effects through Socratic questioning about cultivation theory, agenda-setting, and media influence.",
            "module_prompt": "Help students explore media theories like cultivation theory, agenda-setting, and spiral of silence through discovery-based learning."
        },
        {
            "id": 3,
            "title": "Shared Characteristics of Media", 
            "description": "Common features and patterns across all media types",
            "system_prompt": "Use Socratic questioning to help students identify universal patterns and characteristics that exist across all forms of media.",
            "module_prompt": "Guide discovery of shared media characteristics through comparative analysis and pattern recognition."
        },
        {
            "id": 4,
            "title": "Communication Infrastructure", 
            "description": "Telegraph, telephone, internet, and digital networks",
            "system_prompt": "Lead students to understand the evolution of communication infrastructure through strategic questions about technological development and social impact.",
            "module_prompt": "Explore how communication infrastructure has evolved from telegraph to internet and its societal implications."
        },
        {
            "id": 5,
            "title": "Books: The Birth of Mass Communication", 
            "description": "History, publishing industry, and cultural impact of books",
            "system_prompt": "Guide students to discover how books became the first mass medium and their transformative cultural impact through Socratic inquiry.",
            "module_prompt": "Help students understand the publishing industry, copyright, and how books shaped civilization through strategic questioning."
        },
        {
            "id": 6,
            "title": "News & Newspapers", 
            "description": "News values, gatekeeping, and journalism norms",
            "system_prompt": "Use Socratic questioning to help students understand how news is constructed, what makes something 'newsworthy,' and the role of gatekeepers.",
            "module_prompt": "Explore news values, gatekeeping theory, and journalism ethics through guided discovery."
        },
        {
            "id": 7,
            "title": "Magazines: The Special Interest Medium", 
            "description": "Specialization, audience targeting, and magazine economics",
            "system_prompt": "Guide students to understand how magazines evolved from general interest to specialized publications through strategic questioning.",
            "module_prompt": "Help students discover magazine industry economics, audience segmentation, and the shift to specialization."
        },
        {
            "id": 8,
            "title": "Comic Books: Small Business, Big Impact", 
            "description": "Cultural influence and artistic expression in comics",
            "system_prompt": "Use Socratic questioning to explore how comic books, despite being a small industry, have had significant cultural impact.",
            "module_prompt": "Guide discovery of comic book art, storytelling, and cultural significance through strategic inquiry."
        },
        {
            "id": 9,
            "title": "Photography: Fixing a Shadow", 
            "description": "Visual communication and photographic technology",
            "system_prompt": "Lead students to understand how photography changed human communication and perception through strategic questioning.",
            "module_prompt": "Explore photographic technology, visual communication, and the phrase 'fixing a shadow' through guided discovery."
        },
        {
            "id": 10,
            "title": "Recordings: From Bach to Rock & Rap", 
            "description": "Music industry, cultural reflection, and audio technology",
            "system_prompt": "Guide students to understand how recorded music reflects and shapes culture through Socratic questioning about music industry evolution.",
            "module_prompt": "Help students explore how music recording technology and industry practices have evolved from classical to contemporary genres."
        },
        {
            "id": 11,
            "title": "Motion Pictures: The Start of Mass Entertainment", 
            "description": "Film industry, storytelling, and cinematic influence",
            "system_prompt": "Use strategic questioning to help students understand how motion pictures became the first mass entertainment medium.",
            "module_prompt": "Explore film industry development, storytelling techniques, and cinema's role as a 'dream factory' through guided discovery."
        },
        {
            "id": 12,
            "title": "Radio: The Pervasive Medium", 
            "description": "Broadcasting history, programming, and radio's social role",
            "system_prompt": "Guide students to discover why radio became the most pervasive medium and its unique social role through Socratic questioning.",
            "module_prompt": "Help students understand radio's development, programming evolution, and its role in society through strategic inquiry."
        },
        {
            "id": 13,
            "title": "Television: The Center of Attention", 
            "description": "TV's dominance, programming, and cultural transformation",
            "system_prompt": "Use Socratic questioning to help students understand why television became the dominant medium and its cultural impact.",
            "module_prompt": "Explore television's rise to dominance, programming strategies, and cultural transformation through guided discovery."
        },
        {
            "id": 14,
            "title": "Video Games: The Newest Mass Medium", 
            "description": "Interactive entertainment, gaming culture, and digital play",
            "system_prompt": "Guide students to understand how video games represent a new form of mass communication through strategic questioning.",
            "module_prompt": "Help students explore interactive entertainment, gaming culture, and video games as a communication medium."
        },
        {
            "id": 15,
            "title": "Economic Influencers: Advertising, PR, and Ownership", 
            "description": "Economic forces shaping media content and industry",
            "system_prompt": "Use Socratic questioning to help students understand how economic forces shape media content and industry practices.",
            "module_prompt": "Explore advertising, public relations, and media ownership through guided discovery of economic influences."
        }
    ]
    
    for module_data in modules:
        module = Module(
            id=module_data["id"],
            title=module_data["title"], 
            description=module_data["description"],
            resources="", 
            system_prompt=module_data["system_prompt"],
            module_prompt=module_data["module_prompt"], 
            system_corpus="Core communication theories, media effects research, journalism ethics, digital transformation, media literacy",
            module_corpus="", 
            dynamic_corpus="",
            api_endpoint="https://api.openai.com/v1/chat/completions"
        )
        db.add(module)
    
    db.commit()
    print(f"✅ Auto-populated {len(modules)} Communication Media & Society modules")

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "🎉 Harv Backend - Enhanced Memory-Aware AI Tutoring System",
        "status": "running",
        "version": "4.0.0",
        "course": "Communication Media & Society",
        "features": [
            "4-layer dynamic memory system",
            "Socratic tutoring methodology",
            "15 communication media modules",
            "Enhanced memory-driven responses",
            "Cross-module learning persistence",
            "Real-time context optimization"
        ],
        "enhanced_memory": ENHANCED_MEMORY_AVAILABLE
    }

# Health check with enhanced memory status
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
            "version": "4.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "course": "Communication Media & Society",
            "database": {
                "modules": module_count,
                "users": user_count,
                "conversations": conversation_count,
                "memory_summaries": memory_count
            },
            "openai_configured": has_openai_key,
            "enhanced_memory": ENHANCED_MEMORY_AVAILABLE,
            "memory_system": "active" if ENHANCED_MEMORY_AVAILABLE else "basic"
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

# Additional endpoints for enhanced memory system
@app.get("/system/status")
def system_status():
    """Get detailed system status"""
    return {
        "enhanced_memory": ENHANCED_MEMORY_AVAILABLE,
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "version": "4.0.0",
        "course": "Communication Media & Society",
        "modules": 15,
        "features": {
            "socratic_tutoring": True,
            "memory_persistence": True,
            "cross_module_learning": True,
            "context_optimization": ENHANCED_MEMORY_AVAILABLE
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
