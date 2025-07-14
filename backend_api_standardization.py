#!/usr/bin/env python3
"""
Backend API Standardization Script
Fixes API response formats and adds fallback handling
Run from root directory: python backend_api_standardization.py
"""

import os
import shutil
import re
from datetime import datetime

def create_backup():
    """Create backup of backend directory"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backend_backup_{timestamp}"
    print(f"📁 Creating backup: {backup_dir}")
    shutil.copytree("backend", backup_dir, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    return backup_dir

def update_auth_endpoints():
    """Standardize authentication response format"""
    print("🔐 Standardizing authentication endpoints...")
    
    auth_file = "backend/app/routers/auth.py"
    if not os.path.exists(auth_file):
        print(f"⚠️  {auth_file} not found, creating...")
        create_auth_router()
        return
    
    with open(auth_file, 'r') as f:
        content = f.read()
    
    # Replace accessToken with access_token
    content = re.sub(r'"accessToken":\s*token', '"access_token": token', content)
    content = re.sub(r'accessToken', 'access_token', content)
    
    # Ensure consistent response format
    auth_response_pattern = r'return\s+\{[^}]*"access_token"[^}]*\}'
    if not re.search(auth_response_pattern, content):
        # Add standardized response format
        login_pattern = r'(def login.*?)(return.*?)(\})'
        replacement = r'\1return {"access_token": token, "token_type": "bearer", "user_id": user.id}\3'
        content = re.sub(login_pattern, replacement, content, flags=re.DOTALL)
    
    with open(auth_file, 'w') as f:
        f.write(content)
    
    print("✅ Authentication endpoints standardized")

def create_auth_router():
    """Create standardized auth router if missing"""
    auth_content = '''from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.core.security import verify_password, create_access_token, get_password_hash
from app.schemas import UserCreate, Token

router = APIRouter(prefix="/auth", tags=["authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register new user with standardized response"""
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        name=user_data.name,
        hashed_password=hashed_password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create token
    token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id
    }

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login with standardized response format"""
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": token,
        "token_type": "bearer", 
        "user_id": user.id
    }
'''
    
    os.makedirs("backend/app/routers", exist_ok=True)
    with open("backend/app/routers/auth.py", 'w') as f:
        f.write(auth_content)

def update_chat_endpoints():
    """Standardize chat endpoint response structure"""
    print("💬 Standardizing chat endpoints...")
    
    chat_file = "backend/app/routers/chat.py"
    if not os.path.exists(chat_file):
        print(f"⚠️  {chat_file} not found, creating...")
        create_chat_router()
        return
    
    with open(chat_file, 'r') as f:
        content = f.read()
    
    # Replace 'response' with 'reply' in return statements
    content = re.sub(r'"response":\s*([^,}]+)', r'"reply": \1', content)
    content = re.sub(r'response_text', 'reply_text', content)
    
    with open(chat_file, 'w') as f:
        f.write(content)
    
    print("✅ Chat endpoints standardized")

def create_chat_router():
    """Create standardized chat router with OpenAI fallback"""
    chat_content = '''from fastapi import APIRouter, Depends, HTTPException
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
            reply_text = f"I understand you're asking about {message.message}. " \
                        f"Let me help you explore this topic through questions. " \
                        f"What specific aspect of {module.title.lower()} would you like to focus on?"
        
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
'''
    
    os.makedirs("backend/app/routers", exist_ok=True)
    with open("backend/app/routers/chat.py", 'w') as f:
        f.write(chat_content)

def create_openai_client():
    """Create OpenAI client with fallback handling"""
    print("🤖 Creating OpenAI client with fallback...")
    
    openai_content = '''import openai
import os
import logging
from typing import Optional
from app.models import User, Module, Conversation

logger = logging.getLogger(__name__)

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

async def get_openai_response(
    message: str, 
    module: Module, 
    conversation: Conversation, 
    user: User
) -> str:
    """Get response from OpenAI with fallback handling"""
    
    # Check if API key is configured
    if not openai.api_key or openai.api_key.startswith("sk-proj-fake"):
        logger.info("Using fallback response - no valid OpenAI key")
        return get_fallback_response(message, module)
    
    try:
        # Build context from module and conversation
        system_prompt = module.system_prompt or f"You are a Socratic tutor for {module.title}. Guide students through discovery-based learning by asking thought-provoking questions rather than giving direct answers."
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        
        # Call OpenAI API
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except openai.error.AuthenticationError:
        logger.error("OpenAI authentication failed - using fallback")
        return get_fallback_response(message, module)
        
    except openai.error.RateLimitError:
        logger.warning("OpenAI rate limit exceeded - using fallback")
        return get_fallback_response(message, module)
        
    except Exception as e:
        logger.error(f"OpenAI API error: {e} - using fallback")
        return get_fallback_response(message, module)

def get_fallback_response(message: str, module: Module) -> str:
    """Generate fallback response when OpenAI is unavailable"""
    
    # Socratic fallback responses based on module
    fallback_responses = {
        "introduction": [
            "That's an interesting point about {topic}. What do you think are the key elements that make communication 'mass' communication?",
            "You've raised a good question. How do you think {topic} relates to the broader field of mass communication?",
            "Let's explore that further. What examples from your daily life demonstrate the concept you're asking about?"
        ],
        "history": [
            "Excellent question about {topic}. How do you think this development changed the way people received information?",
            "That's a thoughtful inquiry. What factors do you think contributed to this historical change?",
            "Good observation. How might this historical development compare to changes we see in media today?"
        ],
        "theory": [
            "That's a complex theoretical question about {topic}. What evidence might support or challenge this theory?",
            "Interesting perspective. How do you think this theory applies to modern media situations?",
            "Good point to consider. What are the assumptions underlying this theoretical approach?"
        ]
    }
    
    # Simple keyword matching for module type
    module_type = "introduction"
    if "history" in module.title.lower():
        module_type = "history"
    elif "theory" in module.title.lower():
        module_type = "theory"
    
    import random
    response_template = random.choice(fallback_responses[module_type])
    
    # Extract key topic from message
    topic = message[:50] + "..." if len(message) > 50 else message
    
    return response_template.format(topic=topic)
'''
    
    os.makedirs("backend/app/core", exist_ok=True)
    with open("backend/app/core/openai_client.py", 'w') as f:
        f.write(openai_content)

def update_dependencies():
    """Update requirements.txt with consistent JWT dependencies"""
    print("📦 Updating dependencies...")
    
    requirements_file = "requirements.txt"
    if os.path.exists(requirements_file):
        with open(requirements_file, 'r') as f:
            requirements = f.read()
        
        # Remove conflicting JWT libraries
        requirements = re.sub(r'^PyJWT.*$', '', requirements, flags=re.MULTILINE)
        requirements = re.sub(r'^python-jose.*$', '', requirements, flags=re.MULTILINE)
        
        # Add consistent dependencies
        if 'PyJWT' not in requirements:
            requirements += '\nPyJWT==2.8.0\n'
        if 'openai' not in requirements:
            requirements += 'openai==0.28.1\n'
        if 'python-dotenv' not in requirements:
            requirements += 'python-dotenv==1.0.0\n'
        
        with open(requirements_file, 'w') as f:
            f.write(requirements)
    
    print("✅ Dependencies updated")

def create_schemas():
    """Create/update Pydantic schemas for consistent API responses"""
    print("📋 Creating standardized schemas...")
    
    schemas_content = '''from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int

class ChatMessage(BaseModel):
    message: str
    module_id: int
    conversation_id: Optional[int] = None

class ChatResponse(BaseModel):
    reply: str
    conversation_id: int
    module_id: int
    timestamp: Optional[str] = None

class UserCreate(BaseModel):
    email: str
    name: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    
    class Config:
        from_attributes = True
'''
    
    with open("backend/app/schemas.py", 'w') as f:
        f.write(schemas_content)
    
    print("✅ Schemas created")

def run_standardization():
    """Run all API standardization tasks"""
    print("🔌 BACKEND API STANDARDIZATION")
    print("=" * 50)
    
    backup_dir = create_backup()
    
    try:
        update_auth_endpoints()
        update_chat_endpoints()
        create_openai_client()
        update_dependencies()
        create_schemas()
        
        print("\n" + "=" * 50)
        print("✅ BACKEND API STANDARDIZATION COMPLETE!")
        print("=" * 50)
        print(f"📁 Backup created: {backup_dir}")
        print("🔧 Changes made:")
        print("   ✅ Authentication returns 'access_token' (not 'accessToken')")
        print("   ✅ Chat endpoints return 'reply' (not 'response')")
        print("   ✅ OpenAI client with graceful fallback")
        print("   ✅ Consistent JWT dependencies (PyJWT)")
        print("   ✅ Standardized Pydantic schemas")
        print("\n🧪 Next Steps:")
        print("1. cd backend")
        print("2. pip install -r ../requirements.txt")
        print("3. uvicorn app.main:app --reload")
        print("4. Test: curl -X POST http://127.0.0.1:8000/auth/login")
        print("5. Test: curl -X POST http://127.0.0.1:8000/chat/")
        
    except Exception as e:
        print(f"❌ Error during standardization: {e}")
        print(f"🔄 Restore from backup: mv {backup_dir} backend_failed && mv backend {backup_dir}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_standardization()
    if success:
        print("\n🎯 Ready for Frontend Integration!")
    else:
        print("\n⚠️  Please check errors and try again")
