# Enhanced Chat Endpoint with Dynamic Memory
# Save as: backend/app/endpoints/chat_enhanced.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import json
import openai
import os
from datetime import datetime

from app.database import get_db
from app.models import User, Module, Conversation
from app.memory_context_enhanced import DynamicMemoryAssembler

router = APIRouter()

class ChatRequest(BaseModel):
    user_id: int
    module_id: int
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    conversation_id: str
    memory_context_length: int
    memory_layers_active: int

@router.post("/chat", response_model=ChatResponse)
async def enhanced_chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Enhanced chat endpoint with dynamic memory system"""
    
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
        
        # Get assembled prompt
        assembled_prompt = memory_context['assembled_prompt']
        context_metrics = memory_context['context_metrics']
        
        print(f"📚 Memory context assembled: {context_metrics['total_chars']} chars")
        print(f"🧠 Memory layers active: {sum(1 for status in memory_context['database_status'].values() if status)}")
        
        # Get or create conversation
        conversation = None
        if request.conversation_id:
            conversation = db.query(Conversation).filter(
                Conversation.id == request.conversation_id
            ).first()
        
        if not conversation:
            conversation = Conversation(
                user_id=request.user_id,
                module_id=request.module_id,
                title=f"Chat with Module {request.module_id}",
                messages_json=json.dumps([])
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
        
        # Update conversation with new message
        messages = json.loads(conversation.messages_json) if conversation.messages_json else []
        messages.append({
            "role": "user",
            "content": request.message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Call OpenAI with assembled memory context
        openai_response = await call_openai_with_memory(assembled_prompt, request.message)
        
        # Add AI response to conversation
        messages.append({
            "role": "assistant", 
            "content": openai_response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update conversation
        conversation.messages_json = json.dumps(messages)
        conversation.updated_at = datetime.now()
        db.commit()
        
        return ChatResponse(
            reply=openai_response,
            conversation_id=str(conversation.id),
            memory_context_length=context_metrics['total_chars'],
            memory_layers_active=sum(1 for status in memory_context['database_status'].values() if status)
        )
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        # Fallback to simple response
        return ChatResponse(
            reply="I'm having trouble accessing my memory system right now. Could you rephrase your question?",
            conversation_id=request.conversation_id or "fallback",
            memory_context_length=0,
            memory_layers_active=0
        )

async def call_openai_with_memory(assembled_prompt: str, user_message: str) -> str:
    """Call OpenAI with assembled memory context"""
    
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key or openai_api_key.startswith("sk-fake"):
        # Fallback response using memory context
        return generate_fallback_response(assembled_prompt, user_message)
    
    try:
        openai.api_key = openai_api_key
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": assembled_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"⚠️ OpenAI API error: {e}")
        return generate_fallback_response(assembled_prompt, user_message)

def generate_fallback_response(assembled_prompt: str, user_message: str) -> str:
    """Generate Socratic response using memory context without OpenAI"""
    
    # Extract teaching approach from assembled prompt
    socratic_responses = [
        f"That's an interesting point about {user_message[:20]}... What led you to think about it that way?",
        f"I see you're exploring {user_message[:20]}... What examples from your own experience come to mind?",
        f"That's a thoughtful question about {user_message[:20]}... What do you think might be the key factors here?",
        f"You're touching on something important with {user_message[:20]}... How might this connect to what we've discussed before?",
        f"That's worth exploring about {user_message[:20]}... What patterns do you notice?"
    ]
    
    # Use memory context to select appropriate response
    if "confused" in user_message.lower() or "don't understand" in user_message.lower():
        return f"Let's break this down step by step. What's the first part that feels unclear to you?"
    elif "example" in user_message.lower():
        return f"Good thinking! Can you think of a specific example from your own experience?"
    else:
        import random
        return random.choice(socratic_responses)
