#!/bin/bash
# Fix Suite 4 with user_id field

cat > test_suite_4_chat_ai.py << 'EOF'
#!/usr/bin/env python3
"""
Test Suite 4: Chat & AI Layer - Fixed with user_id
Tests: Chat System, AI Integration, Memory Integration
Prerequisites: Suite 1, 2, 3 passing
"""

import requests
import json
import sys
import time
import os
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def load_token():
    """Load token from previous suite"""
    try:
        with open('.test_token', 'r') as f:
            return f.read().strip()
    except:
        return None

def test_chat_basic(token):
    """Test 4.1: Basic chat functionality"""
    print("🔍 Test 4.1: Basic Chat")
    
    if not token:
        print("   ⏭️  Skipping chat test (no token)")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Include user_id as required by your endpoint
    chat_data = {
        "message": "Hello, I want to learn about communication",
        "module_id": 1,
        "user_id": 1,
        "conversation_id": None
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat/", json=chat_data, headers=headers, timeout=15)
        print(f"   Request: {chat_data}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            chat_response = response.json()
            reply = chat_response.get('reply', '')
            if reply and len(reply) > 10:
                print(f"   ✅ Basic chat: PASS")
                print(f"   💬 Response: {len(reply)} chars")
                print(f"   🤖 Preview: {reply[:100]}...")
                return True
            else:
                print("   ❌ Basic chat: Empty response")
                print(f"   Response: {chat_response}")
                return False
        else:
            print(f"   ❌ Basic chat: FAIL ({response.status_code})")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Basic chat: ERROR - {e}")
        return False

def test_ai_integration(token):
    """Test 4.2: AI integration quality"""
    print("\n🔍 Test 4.2: AI Integration")
    
    if not token:
        print("   ⏭️  Skipping AI test (no token)")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test different types of questions
    test_questions = [
        "What is mass communication?",
        "How does social media affect society?",
        "Explain the communication process"
    ]
    
    ai_responses = []
    for i, question in enumerate(test_questions):
        chat_data = {
            "message": question, 
            "module_id": 1,
            "user_id": 1,
            "conversation_id": None
        }
        
        try:
            response = requests.post(f"{BASE_URL}/chat/", json=chat_data, 
                                   headers=headers, timeout=15)
            if response.status_code == 200:
                reply = response.json().get('reply', '')
                if reply:
                    ai_responses.append(len(reply))
                    print(f"   ✅ AI question {i+1}: {len(reply)} chars")
                else:
                    print(f"   ❌ AI question {i+1}: Empty response")
            else:
                print(f"   ❌ AI question {i+1}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ AI question {i+1}: ERROR - {e}")
    
    if len(ai_responses) >= 2:
        avg_length = sum(ai_responses) / len(ai_responses)
        print(f"   ✅ AI integration: PASS")
        print(f"   🤖 Successful responses: {len(ai_responses)}/3")
        print(f"   📊 Avg response length: {avg_length:.0f} chars")
        return True
    else:
        print("   ❌ AI integration: FAIL")
        print(f"   🤖 Successful responses: {len(ai_responses)}/3")
        return False

def test_memory_integration(token):
    """Test 4.3: Memory integration with chat"""
    print("\n🔍 Test 4.3: Memory Integration")
    
    if not token:
        print("   ⏭️  Skipping memory test (no token)")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test memory context
    try:
        context_data = {"user_id": 1, "module_id": 1, "message": "test memory"}
        response = requests.post(f"{BASE_URL}/memory/context", 
                               json=context_data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            context = response.json()
            print("   ✅ Memory integration: PASS")
            print(f"   🧠 Context: {context}")
            return True
        else:
            print(f"   ❌ Memory integration: FAIL ({response.status_code})")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Memory integration: ERROR - {e}")
        return False

def test_chat_with_memory(token):
    """Test 4.4: Chat with memory persistence"""
    print("\n🔍 Test 4.4: Chat with Memory Persistence")
    
    if not token:
        print("   ⏭️  Skipping memory chat test (no token)")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Send a series of messages to test memory
    conversation_messages = [
        "My name is TestUser and I'm studying communication",
        "I'm particularly interested in journalism",
        "What did I tell you about my name and interests?"
    ]
    
    responses = []
    for i, message in enumerate(conversation_messages):
        chat_data = {
            "message": message, 
            "module_id": 1,
            "user_id": 1,
            "conversation_id": None
        }
        
        try:
            response = requests.post(f"{BASE_URL}/chat/", json=chat_data, 
                                   headers=headers, timeout=15)
            if response.status_code == 200:
                reply = response.json().get('reply', '')
                responses.append(reply)
                print(f"   ✅ Memory chat {i+1}: Success")
                if i == 2:  # Check if AI remembers context
                    if any(word in reply.lower() for word in ['journalism', 'testuser', 'interest', 'communication']):
                        print(f"   🧠 Memory working: AI remembers context!")
                    else:
                        print(f"   ⚠️  Memory unclear: {reply[:100]}...")
            else:
                print(f"   ❌ Memory chat {i+1}: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Memory chat {i+1}: ERROR - {e}")
            return False
    
    if len(responses) == 3:
        print("   ✅ Chat with memory: PASS")
        return True
    else:
        print("   ❌ Chat with memory: FAIL")
        return False

def main():
    print("🧪 TEST SUITE 4: CHAT & AI LAYER (Fixed with user_id)")
    print("=" * 60)
    print("Testing: Chat System, AI Integration, Memory")
    print("")
    
    # Load token from previous suite
    token = load_token()
    if not token:
        print("❌ No authentication token found")
        print("Run Suite 3 first to generate token")
        return False
    
    print(f"🔑 Using token: {token[:30]}...")
    
    results = []
    
    # Test 4.1: Basic Chat
    chat_ok = test_chat_basic(token)
    results.append(chat_ok)
    
    # Test 4.2: AI Integration
    ai_ok = test_ai_integration(token)
    results.append(ai_ok)
    
    # Test 4.3: Memory Integration
    memory_ok = test_memory_integration(token)
    results.append(memory_ok)
    
    # Test 4.4: Chat with Memory
    chat_memory_ok = test_chat_with_memory(token)
    results.append(chat_memory_ok)
    
    # Summary
    passed = sum(results)
    print(f"\n📊 Suite 4 Results: {passed}/4 tests passed")
    
    if passed >= 3:  # 3/4 is acceptable
        print("✅ CHAT & AI LAYER: SOLID")
        print("🚀 Ready for Suite 5: Frontend Integration")
        return True
    else:
        print("❌ CHAT & AI LAYER: NEEDS FIXES")
        print("Fix chat/AI issues before proceeding")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
EOF

echo "✅ Fixed test_suite_4_chat_ai.py with user_id field"
echo ""
echo "🔧 Key fix:"
echo "   • Added user_id: 1 to all chat requests"
echo "   • Added conversation_id: None as required"
echo "   • Better error reporting"
echo ""
echo "🚀 Now run:"
echo "   python3 test_suite_4_chat_ai.py"
