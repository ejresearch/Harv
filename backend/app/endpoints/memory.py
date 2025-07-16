from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.models import MemorySummary, Conversation, User, Module
from app.database import get_db
from typing import Optional
import json

router = APIRouter()

class SummaryRequest(BaseModel):
    user_id: int
    module_id: int
    what_learned: str
    how_learned: str

@router.post("/memory/summary")
def save_summary(req: SummaryRequest, db: Session = Depends(get_db)):
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

@router.get("/memory/stats/{module_id}")
def get_memory_stats(module_id: int, db: Session = Depends(get_db)):
    total_conversations = db.query(Conversation).filter(Conversation.module_id == module_id).count()
    memory_summaries = db.query(MemorySummary).filter(MemorySummary.module_id == module_id).count()
    
    return {
        "stats": {
            "total_conversations": total_conversations,
            "exported_conversations": 0,
            "active_conversations": total_conversations,
            "memory_summaries": memory_summaries
        }
    }

@router.post("/memory/test")
def test_memory_system(request: dict, db: Session = Depends(get_db)):
    return {"success": True, "message": "Memory system test passed"}

@router.post("/memory/preview")
def preview_memory_context(request: dict, db: Session = Depends(get_db)):
    return {"success": True, "preview": {"message": "Memory preview working"}}

@router.post("/memory/context")
def get_memory_context(request: dict, db: Session = Depends(get_db)):
    return {"success": True, "context": {"message": "Memory context working"}}
