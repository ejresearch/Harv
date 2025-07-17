#!/usr/bin/env python3
"""
Fix Backend API Response Formats
"""
import os
import re

def fix_auth_responses():
    """Fix authentication response format"""
    auth_file = "app/auth.py"
    if os.path.exists(auth_file):
        with open(auth_file, 'r') as f:
            content = f.read()
        
        # Fix accessToken -> access_token
        content = re.sub(r'"accessToken":', '"access_token":', content)
        content = re.sub(r'accessToken', 'access_token', content)
        
        with open(auth_file, 'w') as f:
            f.write(content)
        print("   ✅ Fixed auth response format")

def fix_chat_responses():
    """Fix chat response format"""
    for root, dirs, files in os.walk("app"):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                
                # Fix response -> reply in chat endpoints
                if 'chat' in filepath.lower() or 'conversation' in filepath.lower():
                    content = re.sub(r'"response":', '"reply":', content)
                    content = re.sub(r'return.*response.*}', 'return {"reply": response}', content)
                    
                    with open(filepath, 'w') as f:
                        f.write(content)
        print("   ✅ Fixed chat response format")

def fix_cors_config():
    """Fix CORS configuration"""
    main_file = "app/main.py"
    if os.path.exists(main_file):
        with open(main_file, 'r') as f:
            content = f.read()
        
        # Add Vite dev server to CORS origins
        if "http://localhost:5173" not in content:
            content = re.sub(
                r'origins=\[(.*?)\]',
                r'origins=[\1, "http://localhost:5173"]',
                content
            )
        
        with open(main_file, 'w') as f:
            f.write(content)
        print("   ✅ Fixed CORS configuration")

if __name__ == "__main__":
    fix_auth_responses()
    fix_chat_responses()
    fix_cors_config()
