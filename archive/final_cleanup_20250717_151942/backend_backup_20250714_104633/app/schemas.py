"""
Complete Pydantic schemas for Primer Initiative
Drop this file as: app/schemas.py
"""

from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime

# ===== REQUEST MODELS =====

class UserRegistrationRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    reason: Optional[str] = None
    familiarity: Optional[str] = None
    learning_style: Optional[str] = None
    goals: Optional[str] = None
    background: Optional[str] = None

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenRefreshRequest(BaseModel):
    refresh_token: str

# ===== RESPONSE MODELS =====

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class OnboardingResponse(BaseModel):
    reason: Optional[str] = None
    familiarity: Optional[str] = None
    learning_style: Optional[str] = None
    goals: Optional[str] = None
    background: Optional[str] = None

    class Config:
        from_attributes = True

class UserProfileResponse(BaseModel):
    user: UserResponse
    onboarding: Optional[OnboardingResponse] = None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: UserResponse

class MessageResponse(BaseModel):
    message: str
    success: bool = True

# ===== PROGRESS MODELS =====

class ProgressUpdateRequest(BaseModel):
    module_id: int
    completed: bool
    grade: Optional[str] = None

class ProgressResponse(BaseModel):
    id: int
    module_id: int
    completed: bool
    grade: Optional[str] = None
    completion_date: Optional[datetime] = None
    time_spent: int
    attempts: int

    class Config:
        from_attributes = True

class UserStatsResponse(BaseModel):
    total_modules: int
    completed_modules: int
    completion_rate: float
    average_grade: Optional[str] = None
    total_time_spent: int
    progress: List[ProgressResponse]

# ===== CHAT MODELS =====

class ChatRequest(BaseModel):
    user_id: int
    module_id: int
    message: str
    conversation_id: Optional[int] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: int
    message_id: int
    tokens_used: Optional[int] = None
    processing_time: Optional[float] = None

# ===== MEMORY MODELS =====

class MemoryContextRequest(BaseModel):
    user_id: int
    module_id: int
    conversation_id: Optional[int] = None

class MemoryContextResponse(BaseModel):
    system_context: str
    module_context: str
    conversation_context: str
    user_context: str
