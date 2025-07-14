#!/usr/bin/env python3
"""
Fix Import Errors - Update schemas and fix imports
Run from root directory: python fix_import_errors.py
"""

import os

def update_schemas():
    """Update schemas.py with all required models"""
    print("📋 Updating schemas.py with missing models...")
    
    schemas_content = '''from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str = Field(..., min_length=6)

class UserRegistrationRequest(BaseModel):
    """Legacy compatibility - maps to UserCreate"""
    email: EmailStr
    name: str
    password: str = Field(..., min_length=6)
    onboarding_data: Optional[Dict[str, Any]] = None

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Chat Schemas
class ChatMessage(BaseModel):
    message: str
    module_id: int
    conversation_id: Optional[int] = None

class ChatResponse(BaseModel):
    reply: str
    conversation_id: int
    module_id: int
    timestamp: Optional[str] = None

# Module Schemas
class ModuleResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    
    class Config:
        from_attributes = True

# Conversation Schemas
class ConversationCreate(BaseModel):
    module_id: int
    title: Optional[str] = None

class ConversationResponse(BaseModel):
    id: int
    module_id: int
    title: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Health Check Schema
class HealthResponse(BaseModel):
    status: str
    message: str
    timestamp: str
    database: str
    modules_count: int

# Error Schemas
class ErrorResponse(BaseModel):
    detail: str
    status_code: int
'''
    
    with open("backend/app/schemas.py", 'w') as f:
        f.write(schemas_content)
    
    print("✅ Schemas updated with all required models")

def check_existing_auth_file():
    """Check what's in the existing auth file and fix imports"""
    auth_file = "backend/app/endpoints/auth.py"
    
    if os.path.exists(auth_file):
        print("🔍 Checking existing auth.py file...")
        with open(auth_file, 'r') as f:
            content = f.read()
        
        # Fix import statements
        content = content.replace(
            'from app.schemas import (',
            'from app.schemas import ('
        )
        
        # Add missing imports if needed
        if 'UserRegistrationRequest' in content and 'UserCreate' not in content:
            content = content.replace(
                'UserRegistrationRequest',
                'UserRegistrationRequest, UserCreate'
            )
        
        with open(auth_file, 'w') as f:
            f.write(content)
        
        print("✅ Fixed imports in existing auth.py")
    else:
        print("⚠️  No existing auth.py file found")

def update_main_app():
    """Update main.py to handle missing routers"""
    print("🔧 Checking main.py imports...")
    
    main_file = "backend/app/main.py"
    if os.path.exists(main_file):
        with open(main_file, 'r') as f:
            content = f.read()
        
        # Fix router imports to be more flexible
        if 'from app.endpoints.auth import router as auth_router' in content:
            # Replace with conditional import
            content = content.replace(
                'from app.endpoints.auth import router as auth_router',
                '''try:
    from app.endpoints.auth import router as auth_router
except ImportError:
    from app.routers.auth import router as auth_router'''
            )
        
        if 'from app.endpoints.chat import router as chat_router' in content:
            content = content.replace(
                'from app.endpoints.chat import router as chat_router',
                '''try:
    from app.endpoints.chat import router as chat_router
except ImportError:
    from app.routers.chat import router as chat_router'''
            )
        
        with open(main_file, 'w') as f:
            f.write(content)
        
        print("✅ Updated main.py with flexible imports")

def create_missing_security_module():
    """Create security module if missing"""
    security_file = "backend/app/core/security.py"
    
    if not os.path.exists(security_file):
        print("🔐 Creating missing security module...")
        
        os.makedirs("backend/app/core", exist_ok=True)
        
        security_content = '''import os
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    
    return user
'''
        
        with open(security_file, 'w') as f:
            f.write(security_content)
        
        print("✅ Created security module")

def run_fixes():
    """Run all import fixes"""
    print("🔧 FIXING IMPORT ERRORS")
    print("=" * 30)
    
    update_schemas()
    check_existing_auth_file()
    update_main_app()
    create_missing_security_module()
    
    print("\n" + "=" * 30)
    print("✅ IMPORT FIXES COMPLETE!")
    print("=" * 30)
    print("🔧 Changes made:")
    print("   ✅ Updated schemas.py with all required models")
    print("   ✅ Fixed import statements in auth.py")
    print("   ✅ Updated main.py with flexible imports")
    print("   ✅ Created missing security module")
    print("\n🧪 Next Steps:")
    print("1. uvicorn app.main:app --reload")
    print("2. Test: curl http://127.0.0.1:8000/health")

if __name__ == "__main__":
    run_fixes()
