from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.models import Conversation, Module
from app.database import get_db
from openai import OpenAI
import json

router = APIRouter()
client = OpenAI()

class ChatRequest(BaseModel):
    user_id: int
    module_id: int
    message: str

class ChatResponse(BaseModel):
    reply: str

@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    module = db.query(Module).filter(Module.id == req.module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    convo = db.query(Conversation).filter_by(user_id=req.user_id, module_id=req.module_id).first()
    if convo:
        messages = json.loads(convo.messages_json)
    else:
        messages = []

    # Add user message
    messages.append({"role": "user", "content": req.message})

    # Build full messages with system prompt
    full_messages = [{"role": "system", "content": module.system_prompt}] + messages

    # Call OpenAI API (new client)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=full_messages
    )

    gpt_reply = response.choices[0].message.content.strip()

    # Add GPT reply to conversation
    messages.append({"role": "assistant", "content": gpt_reply})

    # Save conversation
    if convo:
        convo.messages_json = json.dumps(messages)
    else:
        convo = Conversation(
            user_id=req.user_id,
            module_id=req.module_id,
            messages_json=json.dumps(messages)
        )
        db.add(convo)

    db.commit()
    return {"reply": gpt_reply}
