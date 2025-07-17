
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional, Union
from pydantic import BaseModel
import json

router = APIRouter()

class LoginRequest(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: str

@router.post("/login")
async def flexible_login(
    request: Request,
    db: Session = Depends(get_db),
    # Try OAuth2 form first
    form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm),
    # Alternative form fields
    email: Optional[str] = Form(None),
    username: Optional[str] = Form(None),
    password: Optional[str] = Form(None)
):
    """Flexible login that accepts JSON, form data, or OAuth2 format"""
    
    try:
        login_email = None
        login_password = None
        
        # Method 1: Try OAuth2 form data
        if hasattr(form_data, 'username') and form_data.username:
            login_email = form_data.username
            login_password = form_data.password
            print(f"🔍 Using OAuth2 form: {login_email}")
        
        # Method 2: Try explicit form fields
        elif email and password:
            login_email = email
            login_password = password
            print(f"🔍 Using form fields: {login_email}")
        
        elif username and password:
            login_email = username
            login_password = password
            print(f"🔍 Using form username: {login_email}")
        
        # Method 3: Try JSON body
        else:
            try:
                body = await request.body()
                if body:
                    data = json.loads(body)
                    login_email = data.get('email') or data.get('username')
                    login_password = data.get('password')
                    print(f"🔍 Using JSON: {login_email}")
            except:
                pass
        
        if not login_email or not login_password:
            print("❌ No valid credentials found")
            raise HTTPException(status_code=422, detail="Email/username and password required")
        
        # Authenticate
        user = authenticate_user(db, login_email, login_password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Create tokens
        tokens = create_user_tokens(user.id)
        
        return {
            "access_token": tokens["access_token"],
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")
