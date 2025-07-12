"""
Enhanced Chat Endpoint with Memory Integration
Replace your entire backend/app/endpoints/chat.py with this file
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.models import Conversation, Module, User
from app.database import get_db
from app.memory_context import MemoryContextAssembler
import openai
import json
import os
from typing import Optional
from datetime import datetime

router = APIRouter()

class ChatRequest(BaseModel):
    user_id: int
    module_id: int
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    conversation_id: int
    grade: Optional[str] = None

@router.post("/", response_model=ChatResponse)
def memory_enhanced_chat(req: ChatRequest, db: Session = Depends(get_db)):
    """Memory-enhanced chat with 4-layer context integration"""
    
    print(f"💬 Memory-enhanced chat: user={req.user_id}, module={req.module_id}")
    print(f"📝 Message: {req.message[:100]}...")
    
    try:
        # Get user and module
        user = db.query(User).filter(User.id == req.user_id).first()
        if not user:
            print(f"❌ User {req.user_id} not found")
            raise HTTPException(status_code=404, detail="User not found")
        
        module = db.query(Module).filter(Module.id == req.module_id).first()
        if not module:
            print(f"❌ Module {req.module_id} not found, creating default")
            # Create default module if it doesn't exist
            module = Module(
                id=req.module_id,
                title=f"Module {req.module_id}",
                description="Mass Communication Module",
                resources="",
                system_prompt="You are Harv, a Socratic tutor for mass communication. Never give direct answers. Always respond with thoughtful questions that guide discovery.",
                module_prompt="Focus on helping students discover concepts through questioning.",
                system_corpus="Core concepts: media theory, communication effects, journalism",
                module_corpus="",
                dynamic_corpus=""
            )
            db.add(module)
            db.commit()
            db.refresh(module)
        
        # Get or create conversation
        conversation = None
        if req.conversation_id:
            try:
                conv_id = int(req.conversation_id) if req.conversation_id != 'default' else None
                if conv_id:
                    conversation = db.query(Conversation).filter(
                        Conversation.id == conv_id,
                        Conversation.user_id == req.user_id
                    ).first()
            except ValueError:
                pass  # conversation_id is not a valid integer
        
        # Parse existing messages
        messages = []
        if conversation and conversation.messages_json:
            try:
                messages = json.loads(conversation.messages_json)
            except json.JSONDecodeError:
                messages = []
        
        # Add user message
        messages.append({"role": "user", "content": req.message})
        
        # Check for API key and generate response
        api_key = os.getenv("OPENAI_API_KEY")
        
        if api_key and api_key.startswith("sk-"):
            print("🧠 Using memory-enhanced GPT response")
            try:
                # Assemble memory context
                memory_assembler = MemoryContextAssembler(db)
                memory_context = memory_assembler.assemble_full_context(
                    user, module, conversation or Conversation()
                )
                
                # Build memory-enhanced prompt
                enhanced_prompt = memory_assembler.build_gpt_prompt(
                    memory_context, req.message
                )
                
                print(f"📚 Memory context assembled: {len(enhanced_prompt)} chars")
                
                # Call OpenAI with memory context
                client = openai.OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": enhanced_prompt[:8000]},  # Truncate if too long
                        {"role": "user", "content": req.message}
                    ],
                    max_tokens=300,
                    temperature=0.7
                )
                gpt_reply = response.choices[0].message.content.strip()
                print(f"✅ Memory-enhanced response generated: {gpt_reply[:50]}...")
                
            except Exception as e:
                print(f"❌ Memory-enhanced GPT error: {e}")
                # Fallback to basic Socratic response
                gpt_reply = f"That's a thoughtful question about '{req.message[:30]}...' What examples from your own media experience might help us explore this concept together?"
        else:
            print("🔄 Using fallback Socratic response (no API key)")
            # Socratic fallback responses
            socratic_responses = [
                f"That's an interesting question about '{req.message[:30]}...' What examples from your own experience might help us explore this concept?",
                f"Before we dive deeper into '{req.message[:30]}...', what do you think are the key factors at play here?",
                f"Good question! Rather than giving you a direct answer about '{req.message[:30]}...', what patterns have you noticed in media that might relate?",
                f"Let me turn this around - if you were explaining '{req.message[:30]}...' to a friend, what would you say?",
                f"Interesting! What current examples from news or social media might demonstrate what you're asking about in '{req.message[:30]}...'?",
                f"That's a perceptive observation. What questions does this raise for you about how media shapes our understanding?",
                f"Excellent thinking! How might this principle apply differently across various demographic groups or cultures?"
            ]
            
            import random
            gpt_reply = random.choice(socratic_responses)
        
        # Add AI response to messages
        messages.append({"role": "assistant", "content": gpt_reply})
        
        # Update or create conversation
        if conversation:
            conversation.messages_json = json.dumps(messages)
            conversation.updated_at = datetime.utcnow()
            print(f"📝 Updated existing conversation {conversation.id}")
        else:
            conversation = Conversation(
                user_id=req.user_id,
                module_id=req.module_id,
                title=f"Discussion - {module.title}",
                messages_json=json.dumps(messages),
                current_grade=None
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            print(f"📝 Created new conversation {conversation.id}")
        
        # Check if conversation should trigger memory extraction
        message_count = len(messages)
        if message_count >= 10 and message_count % 5 == 0:  # Every 5 messages after 10
            print(f"🧠 Triggering memory extraction for conversation {conversation.id}")
            try:
                memory_assembler = MemoryContextAssembler(db)
                summary = memory_assembler.generate_memory_summary(messages)
                conversation.memory_summary = summary
                print(f"✅ Memory summary generated: {summary[:100]}...")
            except Exception as e:
                print(f"⚠️ Memory extraction failed: {e}")
        
        db.commit()
        
        return ChatResponse(
            reply=gpt_reply,
            conversation_id=conversation.id,
            grade=conversation.current_grade
        )
        
    except Exception as e:
        print(f"❌ Memory-enhanced chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@router.get("/health")
def chat_health():
    """Health check for chat endpoint"""
    return {
        "status": "Chat endpoint with memory system is working", 
        "has_openai_key": bool(os.getenv("OPENAI_API_KEY")),
        "memory_system": "active"
    }
