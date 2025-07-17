#!/bin/bash
# Complete Harv Backend Startup Script

echo "🐍 Starting Harv Python Backend..."
echo "=================================="

# Check if we're in the right directory
if [ ! -d "backend" ]; then
    echo "❌ Error: Run this script from the harv root directory"
    exit 1
fi

cd backend

# Check if virtual environment exists
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo "⚠️  No virtual environment found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📦 Installing Python dependencies..."
    pip install fastapi uvicorn sqlalchemy python-jose[cryptography] bcrypt python-multipart openai python-dotenv
else
    echo "🔧 Activating virtual environment..."
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        source .venv/bin/activate
    fi
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "🔧 Creating .env file..."
    cat > .env << 'ENV_EOF'
# Harv Backend Environment Variables
OPENAI_API_KEY=your_openai_api_key_here
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
DATABASE_URL=sqlite:///./harv.db
ENV_EOF
    echo "⚠️  Please add your OpenAI API key to backend/.env"
fi

# Check if app directory exists
if [ ! -d "app" ]; then
    echo "❌ Backend app directory not found. Make sure your FastAPI backend is properly set up."
    exit 1
fi

echo "🚀 Starting FastAPI server..."
echo "Backend will be available at: http://127.0.0.1:8000"
echo "API docs will be at: http://127.0.0.1:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"

python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
