from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.models import Conversation, Module, Document, User
from app.database import get_db
from app.memory_context import MemoryContextAssembler
import openai
import json
import os
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/chat", tags=["chat"])

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatRequest(BaseModel):
    user_id: int
    module_id: int
    message: str
    conversation_id: Optional[int] = None

class ChatResponse(BaseModel):
    reply: str
    conversation_id: int
    grade: Optional[str] = None

@router.post("/", response_model=ChatResponse)
def enhanced_chat(
    req: ChatRequest, 
    db: Session = Depends(get_db)
):
    """Enhanced chat with 4-layer memory system"""
    
    user_id = req.user_id
    
    # Get module
    module = db.query(Module).filter(Module.id == req.module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get or create conversation
    if req.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == req.conversation_id,
            Conversation.user_id == user_id
        ).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = db.query(Conversation).filter_by(
            user_id=user_id, 
            module_id=req.module_id
        ).first()
    
    # Parse existing messages
    if conversation and conversation.messages_json:
        try:
            messages = json.loads(conversation.messages_json)
        except json.JSONDecodeError:
            messages = []
    else:
        messages = []
    
    # Add user message
    messages.append({"role": "user", "content": req.message})
    
    # FANCY MEMORY SYSTEM!
    try:
        memory_assembler = MemoryContextAssembler(db)
        full_context = memory_assembler.assemble_full_context(user, module, conversation or Conversation())
        enhanced_prompt = memory_assembler.build_gpt_prompt(full_context, req.message)
        
        # Call OpenAI with enhanced context
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": enhanced_prompt}
            ]
        )
        gpt_reply = response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"Enhanced memory failed, using fallback: {e}")
        # Fallback to simple system
        system_parts = []
        if module.system_prompt:
            system_parts.append(module.system_prompt)
        if module.module_prompt:
            system_parts.append(f"\nModule Focus:\n{module.module_prompt}")
        
        fallback_prompt = "\n\n".join(system_parts) if system_parts else "You are a helpful AI assistant teaching mass communication."
        full_messages = [{"role": "system", "content": fallback_prompt}] + messages
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=full_messages
        )
        gpt_reply = response.choices[0].message.content.strip()
    
    # Add GPT response
    messages.append({"role": "assistant", "content": gpt_reply})
    
    # Update or create conversation
    if conversation:
        conversation.messages_json = json.dumps(messages)
        conversation.updated_at = datetime.utcnow()
        # Update memory summary if conversation is getting long
        if len(messages) > 20:
            try:
                memory_assembler = MemoryContextAssembler(db)
                conversation.memory_summary = memory_assembler.generate_memory_summary(messages[-10:])
            except:
                pass
    else:
        conversation = Conversation(
            user_id=user_id,
            module_id=req.module_id,
            title=f"Discussion - {module.title}",
            messages_json=json.dumps(messages)
        )
        db.add(conversation)
    
    db.commit()
    db.refresh(conversation)
    
    return ChatResponse(
        reply=gpt_reply,
        conversation_id=conversation.id,
        grade=conversation.current_grade
    )
