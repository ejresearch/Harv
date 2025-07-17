"""
Complete Authentication Endpoints for Primer Initiative - FIXED VERSION
Fixed: Syntax errors and schema issues
"""

from fastapi import Request, APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.auth import (
    authenticate_user, create_user_account, create_user_tokens,
    get_current_user, verify_token, get_user_by_id
)
from app.schemas import (
    UserRegistrationRequest, UserCreate, UserLoginRequest, TokenRefreshRequest,
    UserResponse, MessageResponse
)
from app.models import User, OnboardingSurvey

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ===== AUTHENTICATION ENDPOINTS =====

@router.post("/register")
async def register_user(
    request: UserRegistrationRequest, UserCreate,
    db: Session = Depends(get_db)
):
    """Register new user account - FIXED VERSION"""
    try:
        print(f"DEBUG: Registration attempt - email={request.email}, name={request.name}")
        
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
        
        print(f"DEBUG: User created successfully - ID={user.id}")
        
        # Create tokens
        tokens = create_user_tokens(user.id)
        
        print(f"DEBUG: Tokens created successfully")
        
        # Return complete response (simplified to avoid schema issues)
        return {
            "message": "User registered successfully",
            "success": True,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name
            },
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": tokens["token_type"],
            "expires_in": tokens["expires_in"]
        }
        
    except HTTPException as e:
        print(f"DEBUG: HTTPException during registration: {e.detail}")
        raise e
    except Exception as e:
        print(f"DEBUG: Unexpected error during registration: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login")
async def login_user(request: Request, db: Session = Depends(get_db)):
    """Login user - with debugging"""
    try:
        # Debug: Print request content type and raw body
        content_type = request.headers.get("content-type", "")
        print(f"🔍 Login request content-type: {content_type}")
        
        # Try to get JSON body
        try:
            body = await request.body()
            print(f"🔍 Raw request body: {body}")
            
            if content_type == "application/json":
                import json
                data = json.loads(body)
                print(f"🔍 Parsed JSON data: {data}")
                
                # Extract credentials from JSON
                email = data.get("email") or data.get("username")
                password = data.get("password")
                
            elif "application/x-www-form-urlencoded" in content_type:
                from urllib.parse import parse_qs
                import urllib.parse
                decoded_body = urllib.parse.unquote_plus(body.decode())
                parsed = parse_qs(decoded_body)
                print(f"🔍 Parsed form data: {parsed}")
                
                email = parsed.get("email", [None])[0] or parsed.get("username", [None])[0]
                password = parsed.get("password", [None])[0]
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
                
            if not email or not password:
                return {"error": "Email/username and password required", "status": 422}
                
            print(f"🔍 Extracted credentials - email: {email}")
            
        except Exception as parse_error:
            print(f"❌ Request parsing error: {parse_error}")
            return {"error": "Invalid request format", "status": 422}
        
        # Authenticate user
        user = authenticate_user(db, email, password)
        if not user:
            return {"error": "Invalid credentials", "status": 401}
        
        # Create tokens
        tokens = create_user_tokens(user.id)
        
        return {
            "message": "Login successful",
            "access_token": tokens["access_token"],
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name
            }
        }
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return {"error": str(e), "status": 500}@router.post("/refresh")
async def refresh_token(
    request: TokenRefreshRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    try:
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
        
        return {
            "message": "Token refreshed successfully",
            "success": True,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name
            },
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": tokens["token_type"],
            "expires_in": tokens["expires_in"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.get("/me")
async def get_current_user_profile(
    current_user: User = Depends(get_current_user()),
    db: Session = Depends(get_db)
):
    """Get current user's profile information"""
    try:
        # Get onboarding survey
        onboarding = db.query(OnboardingSurvey).filter(
            OnboardingSurvey.user_id == current_user.id
        ).first()
        
        onboarding_data = None
        if onboarding:
            onboarding_data = {
                "reason": onboarding.reason,
                "familiarity": onboarding.familiarity,
                "learning_style": onboarding.learning_style,
                "goals": onboarding.goals,
                "background": onboarding.background
            }
        
        return {
            "message": "Profile retrieved successfully",
            "success": True,
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "name": current_user.name
            },
            "onboarding": onboarding_data
        }
        
    except Exception as e:
        print(f"DEBUG: Profile retrieval error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve profile"
        )

@router.post("/logout")
async def logout_user(
    current_user: User = Depends(get_current_user())
):
    """Logout user (client should discard tokens)"""
    return {
        "message": "Successfully logged out",
        "success": True
    }

@router.get("/health")
async def auth_health():
    """Authentication system health check"""
    return {
        "status": "healthy",
        "service": "authentication",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Authentication service is running"
    }

# ===== SIMPLIFIED TEST ENDPOINTS =====

@router.post("/test-register")
async def test_register(
    request: UserRegistrationRequest, UserCreate,
    db: Session = Depends(get_db)
):
    """Simplified test registration endpoint"""
    try:
        print(f"TEST: Creating user {request.email}")
        
        # Just create user without complex response schemas
        user = create_user_account(
            db=db,
            email=request.email,
            password=request.password,
            name=request.name
        )
        
        return {
            "message": "Test registration successful",
            "user_id": user.id,
            "email": user.email,
            "name": user.name
        }
        
    except Exception as e:
        print(f"TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {
            "error": str(e),
            "message": "Test registration failed"
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
