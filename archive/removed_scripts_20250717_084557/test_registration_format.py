#!/usr/bin/env python3
"""
Test Registration Format - Debug 422 Errors
"""
import requests
import json

def test_registration_formats():
    """Test different registration formats to find the working one"""
    
    BASE_URL = "http://127.0.0.1:8000"
    
    # Test the exact format the frontend is sending
    frontend_format = {
        "email": "test@example.com",
        "password": "testpass123",
        "name": "Test User",
        "username": "test@example.com",
        "reason": "Learning mass communication",
        "familiarity": "Beginner",
        "learning_style": "Mixed"
    }
    
    print("🧪 Testing frontend registration format...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=frontend_format,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 422:
            data = response.json()
            print(f"   422 Error Details: {data}")
            if 'detail' in data and isinstance(data['detail'], list):
                print("   Missing/Invalid Fields:")
                for error in data['detail']:
                    field = error.get('loc', ['unknown'])[-1]
                    msg = error.get('msg', 'Unknown error')
                    print(f"     - {field}: {msg}")
        elif response.status_code == 200:
            print("   ✅ Registration successful!")
        else:
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_registration_formats()
