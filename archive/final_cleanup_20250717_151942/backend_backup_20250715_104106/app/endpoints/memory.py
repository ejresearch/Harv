"""
Complete Memory Endpoints with Enhanced Features
Replace your entire backend/app/endpoints/memory.py with this file
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.models import MemorySummary, Conversation, User, Module
from app.database import get_db
from app.memory_context import MemoryContextAssembler
from app.auth import get_optional_user, get_current_user_simple, get_current_user_optional
import json
from typing import Optional

router = APIRouter()

class SummaryRequest(BaseModel):
    user_id: int
    module_id: int
    what_learned: str
    how_learned: str

class EditRequest(BaseModel):
    user_id: int
    module_id: int
    what_learned: str = None
    how_learned: str = None

class ResetRequest(BaseModel):
    user_id: int
    module_id: int

class HistoryRequest(BaseModel):
    user_id: int
    module_id: int

# Backward compatible endpoints
@router.post("/memory/summary")
def save_summary(req: SummaryRequest, db: Session = Depends(get_db)):
    """Save memory summary (backward compatible)"""
    summary = db.query(MemorySummary).filter_by(user_id=req.user_id, module_id=req.module_id).first()
    if summary:
        summary.what_learned = req.what_learned
        summary.how_learned = req.how_learned
    else:
        summary = MemorySummary(
            user_id=req.user_id,
            module_id=req.module_id,
            what_learned=req.what_learned,
            how_learned=req.how_learned
        )
        db.add(summary)
    db.commit()
    return {"message": "Summary saved"}

@router.post("/memory/edit")
def edit_summary(req: EditRequest, db: Session = Depends(get_db)):
    """Edit memory summary (backward compatible)"""
    summary = db.query(MemorySummary).filter_by(user_id=req.user_id, module_id=req.module_id).first()
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    if req.what_learned:
        summary.what_learned = req.what_learned
    if req.how_learned:
        summary.how_learned = req.how_learned
    db.commit()
    return {"message": "Summary updated"}

@router.post("/memory/reset")
def reset_memory(req: ResetRequest, db: Session = Depends(get_db)):
    """Reset memory and conversation (backward compatible)"""
    db.query(MemorySummary).filter_by(user_id=req.user_id, module_id=req.module_id).delete()
    db.query(Conversation).filter_by(user_id=req.user_id, module_id=req.module_id).delete()
    db.commit()
    return {"message": "Memory and conversation reset"}

@router.post("/conversation/history")
def conversation_history(req: HistoryRequest, db: Session = Depends(get_db)):
    """Get conversation history (backward compatible)"""
    convo = db.query(Conversation).filter_by(user_id=req.user_id, module_id=req.module_id).first()
    if not convo:
        return {"history": []}
    messages = json.loads(convo.messages_json) if convo.messages_json else []
    return {"history": messages}

@router.post("/export")
def export_conversation(req: HistoryRequest, db: Session = Depends(get_db)):
    """Export conversation (backward compatible)"""
    convo = db.query(Conversation).filter_by(user_id=req.user_id, module_id=req.module_id).first()
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    messages = json.loads(convo.messages_json) if convo.messages_json else []
    text_log = ""
    for msg in messages:
        role = msg['role'].capitalize()
        text_log += f"{role}: {msg['content']}\n\n"
    return {"export": text_log}

# Enhanced memory endpoints
@router.post("/memory/context")
async def get_memory_context(
    user_id: int,
    module_id: int,
    conversation_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Get full 4-layer memory context for debugging/inspection"""
    
    # Use JWT user if available, otherwise use provided user_id
    actual_user_id = current_user.id if current_user else user_id
    
    user = db.query(User).filter(User.id == actual_user_id).first()
    module = db.query(Module).filter(Module.id == module_id).first()
    conversation = None
    
    if conversation_id:
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    
    if not user or not module:
        raise HTTPException(status_code=404, detail="User or module not found")
    
    memory_assembler = MemoryContextAssembler(db)
    context = memory_assembler.assemble_full_context(user, module, conversation or Conversation())
    
    return context

@router.post("/memory/generate-summary")
async def generate_memory_summary(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Generate memory summary for a conversation"""
    
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Verify user owns this conversation
    if current_user and conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if conversation.messages_json:
        messages = json.loads(conversation.messages_json)
        memory_assembler = MemoryContextAssembler(db)
        summary = memory_assembler.generate_memory_summary(messages)
        
        # Update conversation with summary
        conversation.memory_summary = summary
        db.commit()
        
        return {"summary": summary}
    
    return {"summary": "No messages to summarize"}

@router.post("/conversation/finalize")
async def finalize_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Finalize conversation and trigger memory extraction"""
    
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Verify user owns this conversation
    if current_user and conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Mark as finalized
        conversation.finalized = True
        
        # Extract memory if messages exist
        if conversation.messages_json:
            messages = json.loads(conversation.messages_json)
            memory_assembler = MemoryContextAssembler(db)
            
            # Generate comprehensive memory summary
            summary = memory_assembler.generate_memory_summary(messages)
            conversation.memory_summary = summary
            
            # Create memory summary record
            memory_summary = MemorySummary(
                user_id=conversation.user_id,
                module_id=conversation.module_id,
                conversation_id=conversation.id,
                what_learned=summary,
                how_learned="Through Socratic dialogue with AI tutor",
                key_concepts=extract_key_concepts(messages)
            )
            db.add(memory_summary)
        
        db.commit()
        
        return {
            "message": "Conversation finalized and memory extracted",
            "conversation_id": conversation_id,
            "memory_summary": conversation.memory_summary
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Finalization failed: {str(e)}")

@router.get("/memory/stats/{module_id}")
async def get_memory_stats(
    module_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Get memory system statistics for a module"""
    
    # Use JWT user if available, otherwise return general stats
    user_id = current_user.id if current_user else None
    
    # Get conversation statistics
    conv_query = db.query(Conversation).filter(Conversation.module_id == module_id)
    if user_id:
        conv_query = conv_query.filter(Conversation.user_id == user_id)
    
    total_conversations = conv_query.count()
    exported_conversations = conv_query.filter(Conversation.finalized == True).count()
    active_conversations = conv_query.filter(Conversation.finalized == False).count()
    
    # Get memory summary statistics
    memory_query = db.query(MemorySummary).filter(MemorySummary.module_id == module_id)
    if user_id:
        memory_query = memory_query.filter(MemorySummary.user_id == user_id)
    
    memory_summaries = memory_query.count()
    
    return {
        "module_id": module_id,
        "stats": {
            "total_conversations": total_conversations,
            "exported_conversations": exported_conversations,
            "active_conversations": active_conversations,
            "memory_summaries": memory_summaries
        }
    }

@router.post("/memory/test")
async def test_memory_system(
    user_id: int,
    module_id: int,
    test_message: str,
    db: Session = Depends(get_db)
):
    """Test the memory system with a sample message"""
    
    user = db.query(User).filter(User.id == user_id).first()
    module = db.query(Module).filter(Module.id == module_id).first()
    
    if not user or not module:
        raise HTTPException(status_code=404, detail="User or module not found")
    
    # Create test conversation
    test_conversation = Conversation()
    
    # Assemble memory context
    memory_assembler = MemoryContextAssembler(db)
    context = memory_assembler.assemble_full_context(user, module, test_conversation)
    
    # Build test prompt
    enhanced_prompt = memory_assembler.build_gpt_prompt(context, test_message)
    
    return {
        "test_message": test_message,
        "memory_context_length": len(enhanced_prompt),
        "context_preview": enhanced_prompt[:500] + "...",
        "memory_layers": {
            "system_memory": bool(context["system_memory"]["course_corpus"]),
            "module_memory": bool(context["module_memory"]["module_info"]),
            "conversation_memory": len(context["conversation_memory"]["chat_history"]),
            "user_context": len(context["user_context"]["progress"])
        }
    }

@router.post("/memory/preview")
async def preview_memory_context(
    user_id: int,
    module_id: int,
    db: Session = Depends(get_db)
):
    """Preview how memory context is assembled"""
    
    user = db.query(User).filter(User.id == user_id).first()
    module = db.query(Module).filter(Module.id == module_id).first()
    
    if not user or not module:
        raise HTTPException(status_code=404, detail="User or module not found")
    
    # Get latest conversation
    conversation = db.query(Conversation).filter(
        Conversation.user_id == user_id,
        Conversation.module_id == module_id
    ).order_by(Conversation.updated_at.desc()).first()
    
    if not conversation:
        conversation = Conversation()
    
    # Assemble full context
    memory_assembler = MemoryContextAssembler(db)
    context = memory_assembler.assemble_full_context(user, module, conversation)
    
    return {
        "user_name": user.name,
        "module_title": module.title,
        "memory_preview": {
            "system_memory": {
                "course_corpus_items": len(context["system_memory"]["course_corpus"]),
                "has_onboarding": bool(context["system_memory"]["onboarding_data"])
            },
            "module_memory": {
                "title": context["module_memory"]["module_info"]["title"],
                "has_existing_prompts": bool(context["module_memory"]["existing_corpus"]["system_prompt"]),
                "corpus_items": len(context["module_memory"]["module_corpus"])
            },
            "conversation_memory": {
                "title": context["conversation_memory"]["conversation_info"]["title"],
                "message_count": len(context["conversation_memory"]["chat_history"]),
                "memory_summaries": len(context["conversation_memory"]["memory_summaries"])
            },
            "user_context": {
                "progress_items": len(context["user_context"]["progress"]),
                "conversation_history": len(context["user_context"]["conversation_history"])
            }
        }
    }

def extract_key_concepts(messages):
    """Extract key concepts from conversation messages"""
    # Simple keyword extraction from user messages
    user_messages = [msg["content"] for msg in messages if msg.get("role") == "user"]
    
    # Common mass communication concepts
    concepts = []
    keywords = ["media", "communication", "journalism", "digital", "social media", 
                "audience", "message", "effect", "theory", "ethics", "bias"]
    
    for keyword in keywords:
        if any(keyword.lower() in msg.lower() for msg in user_messages):
            concepts.append(keyword)
    
    return ", ".join(concepts[:5])  # Limit to 5 concepts
