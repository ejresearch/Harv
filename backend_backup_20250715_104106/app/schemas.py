from pydantic import BaseModel, EmailStr, Field
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
