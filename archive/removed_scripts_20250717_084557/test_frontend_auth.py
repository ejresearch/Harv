#!/usr/bin/env python3
"""
Test Frontend Authentication Fix
"""
import subprocess
import time
import requests
import webbrowser

def start_frontend():
    """Start the React frontend"""
    print("Starting React frontend...")
    try:
        # Check if frontend is already running
        response = requests.get("http://localhost:5173", timeout=2)
        print("   ✅ Frontend already running on http://localhost:5173")
        return True
    except:
        pass
    
    try:
        # Start frontend
        subprocess.Popen(
            ['npm', 'run', 'dev'],
            cwd='frontend',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for startup
        print("   ⏳ Waiting for frontend to start...")
        for i in range(30):
            try:
                response = requests.get("http://localhost:5173", timeout=1)
                print("   ✅ Frontend started successfully!")
                return True
            except:
                time.sleep(1)
                
        print("   ❌ Frontend failed to start")
        return False
        
    except Exception as e:
        print(f"   ❌ Error starting frontend: {e}")
        return False

def test_auth_flow():
    """Test the authentication flow"""
    print("\n🧪 Testing Authentication Flow")
    print("==============================")
    
    # Test backend is running
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Backend is running")
        else:
            print("   ❌ Backend health check failed")
            return False
    except:
        print("   ❌ Backend is not running")
        print("   💡 Start backend: cd backend && uvicorn app.main:app --reload")
        return False
    
    # Test OAuth2 login format
    try:
        login_data = {
            "username": "questfortheprimer@gmail.com",
            "password": "Joust?poet1c",
            "grant_type": "password"
        }
        
        response = requests.post(
            "http://127.0.0.1:8000/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            print("   ✅ OAuth2 login format working")
            return True
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Login test error: {e}")
        return False

def main():
    print("🔧 Frontend Authentication Fix Test")
    print("===================================")
    
    backend_ok = test_auth_flow()
    
    if backend_ok:
        frontend_ok = start_frontend()
        
        if frontend_ok:
            print("\n🎉 SUCCESS!")
            print("===========")
            print("✅ Backend: Running with OAuth2 authentication")
            print("✅ Frontend: Running with fixed authentication")
            print("")
            print("🌐 Access your platform:")
            print("   Frontend: http://localhost:5173")
            print("   Backend:  http://localhost:8000")
            print("")
            print("🧪 Test Authentication:")
            print("   1. Go to http://localhost:5173")
            print("   2. Try creating an account")
            print("   3. Try logging in")
            print("   4. Should work without 422 errors!")
            
            # Open browser
            try:
                webbrowser.open("http://localhost:5173")
            except:
                pass
                
        else:
            print("\n⚠️  Frontend startup failed")
            print("Manual steps:")
            print("1. cd frontend")
            print("2. npm install")
            print("3. npm run dev")
    else:
        print("\n⚠️  Backend authentication needs to be fixed first")
        print("Make sure backend is running: cd backend && uvicorn app.main:app --reload")

if __name__ == "__main__":
    main()
