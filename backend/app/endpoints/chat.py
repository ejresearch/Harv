# Complete backend/app/endpoints/chat.py
# Enhanced Chat Endpoints with Dynamic Memory System

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Module, Conversation
from pydantic import BaseModel
from openai import OpenAI
import os
import json
from datetime import datetime
from typing import Optional

# Try to import enhanced memory system
try:
    from app.memory_context_enhanced import DynamicMemoryAssembler
    ENHANCED_MEMORY_AVAILABLE = True
    print("✅ Enhanced memory system loaded")
except ImportError:
    ENHANCED_MEMORY_AVAILABLE = False
    print("⚠️ Enhanced memory system not available - using basic chat")

# Create router
router = APIRouter()

# Request models
class ChatRequest(BaseModel):
    user_id: int
    module_id: int
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    conversation_id: str
    memory_metrics: Optional[dict] = None
    enhanced: bool = False

# Configure OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@router.post("/chat/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Regular chat endpoint with basic memory"""
    
    try:
        # Get user and module
        user = db.query(User).filter(User.id == request.user_id).first()
        module = db.query(Module).filter(Module.id == request.module_id).first()
        
        if not user or not module:
            raise HTTPException(status_code=404, detail="User or module not found")
        
        # Get or create conversation
        conversation = None
        if request.conversation_id:
            conversation = db.query(Conversation).filter(
                Conversation.id == request.conversation_id
            ).first()
        
        # Build basic context
        system_prompt = getattr(module, 'system_prompt', '') or f"""
        You are Harv, a Socratic AI tutor for {module.title}. 
        Use strategic questioning to guide students to discover knowledge rather than giving direct answers.
        Help students explore {module.description} through thoughtful inquiry.
        """
        
        module_prompt = getattr(module, 'module_prompt', '') or f"""
        Focus on the learning objectives for {module.title}.
        Use Socratic questioning to help students understand key concepts.
        """
        
        # Combine prompts
        full_prompt = f"{system_prompt}\n\nMODULE FOCUS: {module_prompt}\n\nRemember: Guide through questions, don't give direct answers."
        
        # Call OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and not api_key.startswith("sk-proj-fake"):
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": full_prompt},
                    {"role": "user", "content": request.message}
                ]
            )
            reply = response.choices[0].message.content
        else:
            reply = f"I'm ready to explore {module.title} with you using Socratic questioning! However, I need an OpenAI API key to provide responses. What aspects of {module.title.lower()} would you like to discover together?"
        
        # Save conversation (simplified)
        conversation_id = request.conversation_id or f"conv_{request.user_id}_{request.module_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return ChatResponse(
            reply=reply,
            conversation_id=conversation_id,
            memory_metrics={"total_chars": len(full_prompt), "optimization_score": 50},
            enhanced=False
        )
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@router.post("/chat/enhanced", response_model=ChatResponse)
async def enhanced_chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Enhanced chat with dynamic memory assembly"""
    
    if not ENHANCED_MEMORY_AVAILABLE:
        # Fallback to regular chat
        return await chat(request, db)
    
    try:
        # Initialize dynamic memory assembler
        memory_assembler = DynamicMemoryAssembler(db)
        
        # Assemble dynamic context
        memory_context = memory_assembler.assemble_dynamic_context(
            user_id=request.user_id,
            module_id=request.module_id,
            current_message=request.message,
            conversation_id=request.conversation_id
        )
        
        # Use the assembled prompt for OpenAI
        optimized_prompt = memory_context['assembled_prompt']
        
        # Send to OpenAI with dynamic context
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and not api_key.startswith("sk-proj-fake"):
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": optimized_prompt},
                    {"role": "user", "content": request.message}
                ]
            )
            reply = response.choices[0].message.content
        else:
            reply = f"Enhanced memory system ready! I have {memory_context['context_metrics']['total_chars']} characters of context about your learning journey. However, I need an OpenAI API key to provide intelligent responses. What would you like to explore?"
        
        # Log memory metrics
        metrics = memory_context['context_metrics'] 
        print(f"📊 Enhanced context: {metrics['total_chars']} chars, {metrics['optimization_score']}/100 score")
        
        return ChatResponse(
            reply=reply,
            conversation_id=memory_context['conversation_id'] or f"enhanced_{request.user_id}_{request.module_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            memory_metrics=metrics,
            enhanced=True
        )
        
    except Exception as e:
        print(f"❌ Enhanced chat error: {e}")
        # Fallback to regular chat
        print("🔄 Falling back to regular chat...")
        return await chat(request, db)

@router.get("/memory/enhanced/{module_id}")
async def get_enhanced_memory(
    module_id: int,
    user_id: int = 1,  # Default for testing
    db: Session = Depends(get_db)
):
    """Get enhanced memory data for GUI display"""
    
    if not ENHANCED_MEMORY_AVAILABLE:
        return {
            "error": "Enhanced memory system not available",
            "assembled_prompt": "Install enhanced memory system to see dynamic context",
            "context_metrics": {"total_chars": 0, "optimization_score": 0},
            "memory_layers": {
                "system_data": {"learning_profile": {"style": "adaptive", "pace": "moderate"}},
                "module_data": {"module_info": {"title": f"Module {module_id}"}},
                "conversation_data": {"state": "basic_mode"},
                "prior_knowledge": {"prior_module_insights": []}
            },
            "database_status": {
                "onboarding": False,
                "module_config": False,
                "conversation_analysis": False,
                "cross_module": False
            }
        }
    
    try:
        memory_assembler = DynamicMemoryAssembler(db)
        memory_context = memory_assembler.assemble_dynamic_context(
            user_id=user_id,
            module_id=module_id
        )
        
        print(f"🧠 Memory context assembled for Module {module_id}: {memory_context['context_metrics']['total_chars']} chars")
        
        return memory_context
        
    except Exception as e:
        print(f"❌ Memory endpoint error: {e}")
        return {
            "error": str(e),
            "assembled_prompt": f"Error loading enhanced memory: {str(e)}",
            "context_metrics": {"total_chars": 0, "optimization_score": 0},
            "memory_layers": {
                "system_data": {"learning_profile": {"style": "error", "pace": "unknown"}},
                "module_data": {"module_info": {"title": f"Module {module_id} (Error)"}},
                "conversation_data": {"state": "error_state"},
                "prior_knowledge": {"prior_module_insights": []}
            },
            "database_status": {
                "onboarding": False,
                "module_config": False,
                "conversation_analysis": False,
                "cross_module": False
            }
        }

@router.get("/memory/{user_id}/{module_id}")
async def get_basic_memory(
    user_id: int,
    module_id: int,
    db: Session = Depends(get_db)
):
    """Get basic memory data (fallback for original GUI)"""
    
    try:
        # Get user and module
        user = db.query(User).filter(User.id == user_id).first()
        module = db.query(Module).filter(Module.id == module_id).first()
        
        if not user or not module:
            raise HTTPException(status_code=404, detail="User or module not found")
        
        # Return basic memory structure
        return {
            "memory_layers": {
                "system": {
                    "user_profile": {
                        "learning_style": "adaptive",
                        "pace": "moderate"
                    }
                },
                "module": {
                    "module_info": {
                        "title": module.title,
                        "id": module.id
                    },
                    "teaching_configuration": {
                        "system_prompt": getattr(module, 'system_prompt', ''),
                        "module_prompt": getattr(module, 'module_prompt', '')
                    }
                },
                "conversation": {
                    "state": "ready",
                    "recent_conversations": 0
                },
                "prior": {
                    "total_conversations": 0,
                    "learning_trajectory": "beginning"
                }
            }
        }
        
    except Exception as e:
        print(f"❌ Basic memory error: {e}")
        raise HTTPException(status_code=500, detail=f"Memory error: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "enhanced_memory": ENHANCED_MEMORY_AVAILABLE,
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "timestamp": datetime.now().isoformat()
    }
