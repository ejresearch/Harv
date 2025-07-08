# backend/app/endpoints/chat.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.models import Conversation, Module, Document
from app.database import get_db
import openai
import json
import os

router = APIRouter(prefix="/chat", tags=["chat"])

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatRequest(BaseModel):
    user_id: int
    module_id: int
    message: str

class ChatResponse(BaseModel):
    reply: str

@router.post("/", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    module = db.query(Module).filter(Module.id == req.module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    # Fetch documents for the module
    docs = db.query(Document).filter_by(module_id=req.module_id).all()
    docs_text = "\n\n".join([f"{d.filename}:\n{d.content}" for d in docs])

    # Fetch conversation history
    convo = db.query(Conversation).filter_by(user_id=req.user_id, module_id=req.module_id).first()
    if convo:
        messages = json.loads(convo.messages_json)
    else:
        messages = []

    messages.append({"role": "user", "content": req.message})

    # Compose system prompt + documents
    full_prompt = f"{module.system_prompt}\n\nDocuments:\n{docs_text}"
    full_messages = [{"role": "system", "content": full_prompt}] + messages

    # Call OpenAI
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=full_messages
    )

    gpt_reply = response.choices[0].message.content.strip()
    messages.append({"role": "assistant", "content": gpt_reply})

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

