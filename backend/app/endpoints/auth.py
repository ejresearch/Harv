"""
Complete Authentication Endpoints for Primer Initiative
Drop this file as: app/endpoints/auth.py
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.auth import (
    authenticate_user, create_user_account, create_user_tokens,
    get_current_user, verify_token, get_user_by_id
)
from app.schemas import (
    UserRegistrationRequest, UserLoginRequest, TokenRefreshRequest,
    TokenResponse, UserProfileResponse, MessageResponse,
    UserResponse, OnboardingResponse
)
from app.models import User, OnboardingSurvey

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ===== AUTHENTICATION ENDPOINTS =====

@router.post("/register", response_model=TokenResponse)
async def register_user(
    request: UserRegistrationRequest,
    db: Session = Depends(get_db)
):
    """Register new user account"""
    try:
        # Create user account
        user = create_user_account(
            db=db,
            email=request.email,
            password=request.password,
            name=request.name,
            reason=request.reason,
            familiarity=request.familiarity,
            learning_style=request.learning_style,
            goals=request.goals,
            background=request.background
        )
        
        # Create tokens
        tokens = create_user_tokens(user.id)
        
        # Return complete response
        return TokenResponse(
            **tokens,
            user=UserResponse.from_orm(user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=TokenResponse)
async def login_user(
    request: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """Authenticate user and return tokens"""
    user = authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    tokens = create_user_tokens(user.id)
    
    return TokenResponse(
        **tokens,
        user=UserResponse.from_orm(user)
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: TokenRefreshRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    token_data = verify_token(request.refresh_token)
    
    if not token_data or token_data.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user = get_user_by_id(db, token_data["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    tokens = create_user_tokens(user.id)
    
    return TokenResponse(
        **tokens,
        user=UserResponse.from_orm(user)
    )

@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user()),
    db: Session = Depends(get_db)
):
    """Get current user's profile information"""
    # Get onboarding survey
    onboarding = db.query(OnboardingSurvey).filter(
        OnboardingSurvey.user_id == current_user.id
    ).first()
    
    return UserProfileResponse(
        user=UserResponse.from_orm(current_user),
        onboarding=OnboardingResponse.from_orm(onboarding) if onboarding else None
    )

@router.post("/logout", response_model=MessageResponse)
async def logout_user(
    current_user: User = Depends(get_current_user())
):
    """Logout user (client should discard tokens)"""
    return MessageResponse(
        message="Successfully logged out",
        success=True
    )

@router.get("/health")
async def auth_health():
    """Authentication system health check"""
    return {
        "status": "healthy",
        "service": "authentication",
        "timestamp": datetime.utcnow().isoformat()
    }

# ===== LEGACY COMPATIBILITY ENDPOINTS =====

@router.post("/login_legacy")
async def login_legacy(
    request: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """Legacy login endpoint for backward compatibility"""
    user = authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    tokens = create_user_tokens(user.id)
    
    return {
        "message": "Login successful",
        "user_id": user.id,
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "token_type": tokens["token_type"]
    }
