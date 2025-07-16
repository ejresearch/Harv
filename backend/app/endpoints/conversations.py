
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Conversation, Module
import json

router = APIRouter()

@router.get("/export/{user_id}")
def export_conversations(user_id: int, db: Session = Depends(get_db)):
    """Export conversations for a user"""
    try:
        conversations = db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(Conversation.created_at).all()
        
        export_data = {
            "user_id": user_id,
            "conversations": [
                {
                    "id": conv.id,
                    "message": getattr(conv, 'message', 'N/A'),
                    "response": getattr(conv, 'response', 'N/A'),
                    "module_id": conv.module_id,
                    "created_at": str(conv.created_at)
                }
                for conv in conversations
            ]
        }
        
        return export_data
    except Exception as e:
        return {"conversations": []}
