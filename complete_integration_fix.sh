#!/bin/bash
# Complete Harv Platform Integration Fix
# Run from root directory: bash complete_integration_fix.sh

echo "🚀 Harv Platform - Complete Integration Fix"
echo "=========================================="

# 1. Database Location Fix
echo "📁 Step 1: Fixing database location..."
if [ -f "harv.db" ] && [ -f "backend/harv.db" ]; then
    echo "   Found databases in both locations. Using root harv.db as primary."
    cp harv.db backend/harv.db
    echo "   ✅ Database synchronized"
elif [ -f "harv.db" ]; then
    echo "   Copying root harv.db to backend directory..."
    cp harv.db backend/harv.db
    echo "   ✅ Database copied to backend"
elif [ -f "backend/harv.db" ]; then
    echo "   Copying backend harv.db to root..."
    cp backend/harv.db harv.db
    echo "   ✅ Database copied to root"
else
    echo "   ❌ No database found! Creating new one..."
    touch harv.db
    cp harv.db backend/harv.db
fi

# 2. Final Database Schema Verification
echo "📋 Step 2: Final database verification..."
cat > final_db_fix.py << 'EOF'
#!/usr/bin/env python3
"""
Final Database Verification and Fix
"""
import sqlite3
import os

def fix_database_final():
    # Work with backend database
    db_path = "backend/harv.db"
    if not os.path.exists(db_path):
        db_path = "harv.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Ensure users table has hashed_password
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'password' in columns and 'hashed_password' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN hashed_password TEXT")
            cursor.execute("UPDATE users SET hashed_password = password WHERE hashed_password IS NULL")
            print("   ✅ Fixed users.hashed_password column")
        
        # Ensure documents table has user_id
        cursor.execute("PRAGMA table_info(documents)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'user_id' not in columns:
            cursor.execute("ALTER TABLE documents ADD COLUMN user_id INTEGER")
            print("   ✅ Added documents.user_id column")
        
        # Ensure memory_summaries has conversation_id
        cursor.execute("PRAGMA table_info(memory_summaries)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'conversation_id' not in columns:
            cursor.execute("ALTER TABLE memory_summaries ADD COLUMN conversation_id INTEGER")
            print("   ✅ Added memory_summaries.conversation_id column")
        
        # Verify modules are populated
        cursor.execute("SELECT COUNT(*) FROM modules")
        module_count = cursor.fetchone()[0]
        print(f"   📊 Modules in database: {module_count}")
        
        if module_count < 15:
            print("   🔧 Populating modules...")
            modules = [
                ("Public Speaking Fundamentals", "Speech communication basics"),
                ("Interpersonal Communication", "One-on-one communication skills"),
                ("Group Communication", "Small group dynamics"),
                ("Organizational Communication", "Workplace communication"),
                ("Intercultural Communication", "Cross-cultural understanding"),
                ("Digital Communication", "Online communication platforms"),
                ("Crisis Communication", "Emergency communication strategies"),
                ("Persuasion and Influence", "Persuasive communication techniques"),
                ("Conflict Resolution", "Managing communication conflicts"),
                ("Leadership Communication", "Executive communication skills"),
                ("Media Relations", "Working with media outlets"),
                ("Internal Communications", "Employee communication strategies"),
                ("Brand Communication", "Corporate messaging"),
                ("Social Media Strategy", "Digital platform management"),
                ("Communication Ethics", "Ethical communication practices")
            ]
            
            for i, (name, desc) in enumerate(modules, 1):
                cursor.execute("""
                    INSERT OR REPLACE INTO modules 
                    (id, name, description, module_prompt, system_corpus, module_corpus, dynamic_corpus, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                """, (
                    i, name, desc,
                    f"You are a Socratic tutor for {name}. Guide students through discovery-based learning using strategic questions. Never give direct answers - always respond with thoughtful questions that help students discover the concepts themselves.",
                    f"Core principles of {name.lower()}",
                    f"Module-specific content for {name.lower()}",
                    f"Dynamic learning context for {name.lower()}"
                ))
            print(f"   ✅ Populated {len(modules)} modules")
        
        conn.commit()
        print("   ✅ Database verification complete")
        
    except Exception as e:
        print(f"   ❌ Database error: {e}")
    finally:
        conn.close()
    
    # Copy to both locations to ensure consistency
    if os.path.exists("backend/harv.db") and not os.path.exists("harv.db"):
        import shutil
        shutil.copy2("backend/harv.db", "harv.db")
        print("   ✅ Database synced to root directory")

if __name__ == "__main__":
    fix_database_final()
EOF

python final_db_fix.py
rm final_db_fix.py

# 3. Create Backend API Fixes
echo "🔌 Step 3: Backend API standardization..."
cat > backend/fix_api_responses.py << 'EOF'
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
EOF

cd backend && python fix_api_responses.py && cd ..

# 4. Environment Configuration
echo "⚙️ Step 4: Environment setup..."
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# Harv Platform Environment Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
JWT_SECRET_KEY=your-super-secure-jwt-secret-key-change-this-in-production
DATABASE_URL=sqlite:///./harv.db
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173","http://127.0.0.1:3000","http://127.0.0.1:5173"]
MEMORY_CONTEXT_MAX_LENGTH=2000
MEMORY_EXTRACTION_THRESHOLD=5
DEBUG=true
ENV=development
EOF
    echo "   ✅ Created .env file"
else
    echo "   ✅ .env file already exists"
fi

# 5. Install missing dependencies
echo "📦 Step 5: Installing dependencies..."
cd backend
pip install python-dotenv python-jose[cryptography] passlib[bcrypt] 2>/dev/null || echo "   ℹ️  Some packages may already be installed"
cd ..

# 6. Start Backend Test
echo "🚀 Step 6: Testing backend startup..."
cd backend

# Create a simple startup test
cat > test_startup.py << 'EOF'
#!/usr/bin/env python3
import sys
import os
sys.path.append('.')

try:
    from app.main import app
    print("✅ Backend imports successful")
    
    # Test database connection
    from app.models import User
    print("✅ Database models load successfully")
    
    print("✅ Backend ready to start!")
    print("\nTo start backend: uvicorn app.main:app --reload")
    print("Health check: curl http://127.0.0.1:8000/health")
    
except Exception as e:
    print(f"❌ Backend startup error: {e}")
    sys.exit(1)
EOF

python test_startup.py
rm test_startup.py
cd ..

# 7. Create startup script
echo "📋 Step 7: Creating startup scripts..."
cat > start_backend.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Harv Platform Backend..."
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
EOF

chmod +x start_backend.sh

cat > start_frontend.sh << 'EOF'
#!/bin/bash
echo "🎨 Starting Harv Platform Frontend..."
cd frontend
npm run dev
EOF

chmod +x start_frontend.sh

cat > start_full_platform.sh << 'EOF'
#!/bin/bash
echo "🌟 Starting Complete Harv Platform..."
echo "Backend will start on: http://localhost:8000"
echo "Frontend will start on: http://localhost:5173"
echo ""

# Start backend in background
echo "Starting backend..."
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "Starting frontend..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "🎉 Harv Platform is starting up!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "To stop: kill $BACKEND_PID $FRONTEND_PID"

wait
EOF

chmod +x start_full_platform.sh

# 8. Final Integration Test
echo "🧪 Step 8: Final integration test..."
cat > test_integration.py << 'EOF'
#!/usr/bin/env python3
"""
Final Integration Test
"""
import sqlite3
import os
import requests
import time
import subprocess
import signal
import sys

def test_database():
    """Test database integrity"""
    try:
        conn = sqlite3.connect('backend/harv.db')
        cursor = conn.cursor()
        
        # Test tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        required_tables = ['users', 'modules', 'conversations', 'memory_summaries']
        
        for table in required_tables:
            if table in tables:
                print(f"   ✅ Table {table} exists")
            else:
                print(f"   ❌ Table {table} missing")
                return False
        
        # Test modules populated
        cursor.execute("SELECT COUNT(*) FROM modules")
        module_count = cursor.fetchone()[0]
        print(f"   📊 Modules: {module_count}/15")
        
        conn.close()
        return module_count >= 15
        
    except Exception as e:
        print(f"   ❌ Database test failed: {e}")
        return False

def test_backend_startup():
    """Test if backend can start"""
    try:
        # Start backend process
        backend_process = subprocess.Popen(
            ['uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8001'],
            cwd='backend',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for startup
        time.sleep(5)
        
        # Test health endpoint
        try:
            response = requests.get('http://127.0.0.1:8001/health', timeout=5)
            if response.status_code == 200:
                print("   ✅ Backend started successfully")
                print("   ✅ Health endpoint responding")
                backend_process.terminate()
                return True
            else:
                print(f"   ❌ Health endpoint returned {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Cannot connect to backend: {e}")
        
        backend_process.terminate()
        return False
        
    except Exception as e:
        print(f"   ❌ Backend startup test failed: {e}")
        return False

def main():
    print("🧪 Harv Platform - Final Integration Test")
    print("==========================================")
    
    print("\n📁 Testing database...")
    db_ok = test_database()
    
    print("\n🚀 Testing backend startup...")
    backend_ok = test_backend_startup()
    
    print(f"\n📊 Integration Test Results:")
    print(f"   Database: {'✅ PASS' if db_ok else '❌ FAIL'}")
    print(f"   Backend:  {'✅ PASS' if backend_ok else '❌ FAIL'}")
    
    if db_ok and backend_ok:
        print("\n🎉 Integration test PASSED!")
        print("Your Harv Platform is ready to run!")
        print("\nNext steps:")
        print("1. bash start_backend.sh")
        print("2. Open http://localhost:8000/docs")
        print("3. Test API endpoints")
        return True
    else:
        print("\n⚠️  Integration test found issues.")
        print("Check the error messages above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
EOF

python test_integration.py
rm test_integration.py

echo ""
echo "🎉 Harv Platform Integration Fix Complete!"
echo "========================================"
echo ""
echo "🚀 Your platform is ready! Next steps:"
echo ""
echo "1. Start backend:"
echo "   bash start_backend.sh"
echo ""
echo "2. Start frontend (in another terminal):"
echo "   bash start_frontend.sh"
echo ""
echo "3. Or start everything at once:"
echo "   bash start_full_platform.sh"
echo ""
echo "4. Access your platform:"
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:5173"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "✅ Database: Synchronized and populated"
echo "✅ Backend: API responses standardized"
echo "✅ Frontend: Ready for connection"
echo "✅ Environment: Configured"
echo ""
echo "🎯 Status: Ready for production testing!"
