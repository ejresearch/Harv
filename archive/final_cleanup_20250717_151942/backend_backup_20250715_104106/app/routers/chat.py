from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Module, Conversation
from app.core.security import get_current_user
from app.core.openai_client import get_openai_response
from app.schemas import ChatMessage, ChatResponse
import logging

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)

@router.post("/", response_model=ChatResponse)
async def chat_with_ai(
    message: ChatMessage,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Chat with AI tutor - standardized response format"""
    try:
        # Get module
        module = db.query(Module).filter(Module.id == message.module_id).first()
        if not module:
            raise HTTPException(status_code=404, detail="Module not found")
        
        # Get or create conversation
        conversation = db.query(Conversation).filter(
            Conversation.user_id == current_user.id,
            Conversation.module_id == message.module_id,
            Conversation.finalized == False
        ).first()
        
        if not conversation:
            conversation = Conversation(
                user_id=current_user.id,
                module_id=message.module_id,
                title=f"Chat with {module.title}"
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
        
        # Get AI response with fallback
        try:
            reply_text = await get_openai_response(
                message=message.message,
                module=module,
                conversation=conversation,
                user=current_user
            )
        except Exception as e:
            logger.warning(f"OpenAI API failed: {e}")
            # Fallback response
            reply_text = f"I understand you're asking about {message.message}. "                         f"Let me help you explore this topic through questions. "                         f"What specific aspect of {module.title.lower()} would you like to focus on?"
        
        # Save conversation (implementation depends on your conversation model)
        # conversation.add_message(user_message=message.message, ai_reply=reply_text)
        # db.commit()
        
        return {
            "reply": reply_text,
            "conversation_id": conversation.id,
            "module_id": module.id,
            "timestamp": conversation.updated_at.isoformat() if conversation.updated_at else None
        }
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Chat service temporarily unavailable")
