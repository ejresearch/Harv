# backend/app/auth_working.py
"""
WORKING Authentication System - CREATE NEW FILE
This replaces the complex auth system with a simple working version
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext
import os
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)

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
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)  # 7 days
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            return None
        return {"user_id": int(user_id), "type": payload.get("type")}
    except jwt.ExpiredSignatureError:
        return None
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
            onboarding_data=onboarding_data.get('onboarding_data', ''),  # Keep compatibility
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(user)
        db.flush()  # Get user ID without committing
        
        # Create onboarding survey if data provided
        if any(onboarding_data.get(key) for key in ['reason', 'familiarity', 'learning_style', 'goals', 'background']):
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
        print(f"Registration error: {e}")  # For debugging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user account"
        )

def create_user_tokens(user_id: int) -> Dict[str, Any]:
    """Create token set for user"""
    access_token = create_access_token({"sub": str(user_id)})
    refresh_token = create_refresh_token({"sub": str(user_id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

# Import get_db to avoid circular imports
def get_db():
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Working dependency functions
def get_current_user():
    """Get current user dependency that actually works"""
    def _get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ):
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token_data = verify_token(credentials.credentials)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = get_user_by_id(db, token_data["user_id"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
    
    return _get_current_user

def get_optional_user():
    """Optional user dependency that works"""
    def _get_optional_user(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        db: Session = Depends(get_db)
    ):
        if not credentials:
            return None
        
        token_data = verify_token(credentials.credentials)
        if not token_data:
            return None
        
        return get_user_by_id(db, token_data["user_id"])
    
    return _get_optional_user
