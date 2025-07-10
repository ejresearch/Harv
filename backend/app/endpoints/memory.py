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

# NEW: Enhanced memory endpoints
@router.post("/memory/context")
async def get_memory_context(
    user_id: int,
    module_id: int,
    conversation_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_simple)
):
    """NEW: Get full 4-layer memory context for debugging/inspection"""
    
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
    current_user = Depends(get_current_user_simple)
):
    """NEW: Generate memory summary for a conversation"""
    
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
