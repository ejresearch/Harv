"""
Simple Working Authentication Module with PERMANENT TOKENS
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext
import os
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import secrets

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password with timing attack protection"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """Hash password securely"""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any]) -> str:
    """Create PERMANENT JWT access token (NO EXPIRATION)"""
    to_encode = data.copy()
    
    # Add issued at time but NO expiration
    to_encode.update({
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create PERMANENT JWT refresh token (NO EXPIRATION)"""
    to_encode = data.copy()
    
    # Add issued at time but NO expiration
    to_encode.update({
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token and return payload (NO EXPIRATION CHECK)"""
    try:
        # Decode without expiration verification
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        user_id = payload.get("sub")
        token_type = payload.get("type")
        
        if not user_id:
            return None
            
        return {
            "user_id": int(user_id),
            "type": token_type,
            "iat": payload.get("iat")
        }
    except jwt.JWTError:
        return None

def get_user_by_id(db: Session, user_id: int):
    """Get user by ID with error handling"""
    try:
        from app.models import User
        return db.query(User).filter(User.id == user_id).first()
    except Exception:
        return None

def get_user_by_email(db: Session, email: str):
    """Get user by email with error handling"""
    try:
        from app.models import User
        return db.query(User).filter(User.email == email.lower()).first()
    except Exception:
        return None

def authenticate_user(db: Session, email: str, password: str):
    """Authenticate user with comprehensive security checks"""
    try:
        user = get_user_by_email(db, email)
        if not user:
            # Prevent timing attacks
            pwd_context.verify("dummy", "$2b$12$dummy.hash.to.prevent.timing.attacks")
            return None
            
        if not verify_password(password, user.hashed_password):
            return None
            
        return user
    except Exception:
        return None

def create_user_account(db: Session, email: str, password: str, name: str, **onboarding_data):
    """Create new user account with proper error handling"""
    try:
        from app.models import User, OnboardingSurvey
        
        # Check if user already exists
        existing_user = get_user_by_email(db, email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        hashed_password = get_password_hash(password)
        user = User(
            email=email.lower(),
            hashed_password=hashed_password,
            name=name,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(user)
        db.flush()
        
        # Create onboarding survey if data provided
        if onboarding_data:
            survey = OnboardingSurvey(
                user_id=user.id,
                reason=onboarding_data.get('reason'),
                familiarity=onboarding_data.get('familiarity'),
                learning_style=onboarding_data.get('learning_style'),
                goals=onboarding_data.get('goals'),
                background=onboarding_data.get('background'),
                created_at=datetime.utcnow()
            )
            db.add(survey)
        
        db.commit()
        db.refresh(user)
        return user
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user account"
        )

def create_user_tokens(user_id: int) -> Dict[str, Any]:
    """Create PERMANENT token set for user"""
    access_token = create_access_token({"sub": str(user_id)})
    refresh_token = create_refresh_token({"sub": str(user_id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": "never"  # PERMANENT!
    }

# Missing functions for auth endpoints
def get_current_user():
    """Placeholder - auth endpoints need this"""
    from fastapi import Depends, HTTPException, status
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from app.database import get_db
    
    security = HTTPBearer()
    
    def _get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ):
        token_data = verify_token(credentials.credentials)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user = get_user_by_id(db, token_data["user_id"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
    
    return _get_current_user

# ALL MISSING FUNCTIONS FOR ENDPOINTS
def get_optional_user():
    """Optional user dependency"""
    from fastapi import Depends
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from app.database import get_db
    
    security = HTTPBearer(auto_error=False)
    
    def _get_optional_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ):
        if not credentials:
            return None
        
        token_data = verify_token(credentials.credentials)
        if not token_data:
            return None
        
        return get_user_by_id(db, token_data["user_id"])
    
    return _get_optional_user

def get_current_user_simple():
    """Simple user dependency"""
    return get_optional_user()

def get_current_user_optional():
    """Optional user dependency (alias)"""
    return get_optional_user()
