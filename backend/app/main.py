from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.endpoints import auth, modules, chat, memory, documents, progress
from datetime import datetime

app = FastAPI(
    title="Harv Backend Enhanced",
    description="Enhanced GPT-powered modules with JWT auth and 4-layer memory",
    version="1.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(auth.router)
app.include_router(modules.router)
app.include_router(chat.router)
app.include_router(memory.router)
app.include_router(documents.router)
app.include_router(progress.router)  # NEW

# Health check endpoints
@app.get("/")
def root():
    return {
        "message": "Harv backend enhanced with Priority 1 features",
        "version": "1.1.0",
        "features": [
            "JWT Authentication",
            "4-Layer Memory System", 
            "Progress Tracking",
            "Enhanced Database Schema",
            "Backward Compatible"
        ]
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }
