#!/usr/bin/env python3
"""
Fix 422 Authentication Errors
Run from root directory: python fix_422_auth_errors.py
"""

import os
import re

def debug_auth_endpoint():
    """Add debug logging to auth endpoint"""
    auth_file = "backend/app/endpoints/auth.py"
    
    if not os.path.exists(auth_file):
        print("❌ Auth file not found")
        return
    
    with open(auth_file, 'r') as f:
        content = f.read()
    
    # Add debug logging for request data
    debug_login = '''
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
        return {"error": str(e), "status": 500}
'''
    
    # Replace the existing login endpoint
    pattern = r'@router\.post\("/login"\).*?(?=@router\.|$)'
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, debug_login.strip(), content, flags=re.DOTALL)
        print("✅ Updated login endpoint with debugging")
    else:
        # If pattern doesn't match, append the new endpoint
        content += "\n\n" + debug_login
        print("✅ Added debug login endpoint")
    
    # Add necessary imports
    if "from fastapi import Request" not in content:
        content = content.replace("from fastapi import", "from fastapi import Request,")
    
    with open(auth_file, 'w') as f:
        f.write(content)
    
    print("✅ Auth endpoint updated with debugging")

def create_flexible_login_endpoint():
    """Create a flexible login endpoint that accepts multiple formats"""
    
    flexible_auth = '''
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
'''
    
    # Write the flexible auth file
    with open("backend/app/endpoints/flexible_auth.py", 'w') as f:
        f.write(flexible_auth)
    
    print("✅ Created flexible authentication endpoint")

def test_auth_endpoints():
    """Test the auth endpoints with different formats"""
    
    test_script = '''
#!/usr/bin/env python3
"""
Test Authentication Endpoints
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_login_formats():
    """Test different login formats"""
    
    credentials = {
        "email": "questfortheprimer@gmail.com",
        "password": "Joust?poet1c"
    }
    
    print("🧪 Testing Login Formats")
    print("========================")
    
    # Test 1: JSON format
    print("\\n1. Testing JSON format...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=credentials,
            headers={"Content-Type": "application/json"}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text}")
        else:
            print("   ✅ JSON login successful")
    except Exception as e:
        print(f"   ❌ JSON login error: {e}")
    
    # Test 2: Form data format
    print("\\n2. Testing form data...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data=credentials,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text}")
        else:
            print("   ✅ Form login successful")
    except Exception as e:
        print(f"   ❌ Form login error: {e}")
    
    # Test 3: OAuth2 format with username
    print("\\n3. Testing OAuth2 format...")
    try:
        oauth_data = {
            "username": credentials["email"],
            "password": credentials["password"],
            "grant_type": "password"
        }
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data=oauth_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text}")
        else:
            print("   ✅ OAuth2 login successful")
    except Exception as e:
        print(f"   ❌ OAuth2 login error: {e}")

if __name__ == "__main__":
    test_login_formats()
'''
    
    with open("test_auth_formats.py", 'w') as f:
        f.write(test_script)
    
    print("✅ Created auth testing script")

def main():
    print("🔧 Fixing 422 Authentication Errors")
    print("====================================")
    
    print("\n1. Adding debug logging to auth endpoint...")
    debug_auth_endpoint()
    
    print("\n2. Creating flexible login endpoint...")
    create_flexible_login_endpoint()
    
    print("\n3. Creating auth testing script...")
    test_auth_endpoints()
    
    print("\n✅ Fix complete!")
    print("\nNext steps:")
    print("1. Restart your backend: cd backend && uvicorn app.main:app --reload")
    print("2. Test auth formats: python test_auth_formats.py")
    print("3. Check backend logs for debug output")

if __name__ == "__main__":
    main()
