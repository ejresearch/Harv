#!/usr/bin/env python3
"""
Simple Chat Test - Test chat endpoint directly
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_chat_direct():
    """Test chat endpoint directly with different formats"""
    
    # Load token
    try:
        with open('.test_token', 'r') as f:
            token = f.read().strip()
    except:
        print("❌ No token found - run Suite 3 first")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test different formats based on your schema
    test_formats = [
        # Format 1: All required fields
        {"message": "Hello", "module_id": 1, "conversation_id": None},
        
        # Format 2: Without conversation_id
        {"message": "Hello", "module_id": 1},
        
        # Format 3: With conversation_id as integer
        {"message": "Hello", "module_id": 1, "conversation_id": 1},
        
        # Format 4: Different field names
        {"text": "Hello", "module_id": 1},
        {"content": "Hello", "module_id": 1},
        {"msg": "Hello", "module_id": 1},
    ]
    
    print("🔍 TESTING CHAT ENDPOINT FORMATS")
    print("=" * 50)
    
    for i, chat_data in enumerate(test_formats, 1):
        print(f"\n🔍 Test {i}: {chat_data}")
        
        try:
            response = requests.post(f"{BASE_URL}/chat/", 
                                   json=chat_data, 
                                   headers=headers, 
                                   timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ SUCCESS!")
                print(f"   Response: {result}")
                print(f"   Reply: {result.get('reply', 'No reply field')}")
                break
            else:
                print(f"   ❌ Error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    # Test OpenAI availability
    print(f"\n🔍 TESTING OPENAI AVAILABILITY")
    print("=" * 50)
    
    import os
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"   ✅ OpenAI API key found: {api_key[:20]}...")
    else:
        print("   ❌ OpenAI API key not found")
        print("   💡 Set with: export OPENAI_API_KEY='your-key'")

if __name__ == "__main__":
    test_chat_direct()
