from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.models import MemorySummary, Conversation
from app.database import get_db
import json

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
    db.query(MemorySummary).filter_by(user_id=req.user_id, module_id=req.module_id).delete()
    db.query(Conversation).filter_by(user_id=req.user_id, module_id=req.module_id).delete()
    db.commit()
    return {"message": "Memory and conversation reset"}

@router.post("/conversation/history")
def conversation_history(req: HistoryRequest, db: Session = Depends(get_db)):
    convo = db.query(Conversation).filter_by(user_id=req.user_id, module_id=req.module_id).first()
    if not convo:
        return {"history": []}
    messages = json.loads(convo.messages_json)
    return {"history": messages}

@router.post("/export")
def export_conversation(req: HistoryRequest, db: Session = Depends(get_db)):
    convo = db.query(Conversation).filter_by(user_id=req.user_id, module_id=req.module_id).first()
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    messages = json.loads(convo.messages_json)
    text_log = ""
    for msg in messages:
        role = msg['role'].capitalize()
        text_log += f"{role}: {msg['content']}\n\n"
    return {"export": text_log}

