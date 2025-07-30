#!/bin/bash
# HARV Quick Start Script
# This script sets up and starts the HARV platform

echo "🌱 HARV Quick Start Setup"
echo "========================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+"
    exit 1
fi

echo "✅ Prerequisites checked"

# Check for OpenAI API key
if [ -z "$1" ]; then
    echo ""
    echo "⚠️  No OpenAI API key provided"
    echo "Usage: bash quickstart.sh YOUR_OPENAI_API_KEY"
    echo ""
    echo "To get an API key:"
    echo "1. Go to https://platform.openai.com/api-keys"
    echo "2. Create a new API key"
    echo "3. Run: bash quickstart.sh sk-proj-your-api-key-here"
    echo ""
    exit 1
fi

OPENAI_KEY=$1
echo "🔑 OpenAI API key provided"

# Create virtual environment if it doesn't exist
if [ ! -d "harv_venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv harv_venv
fi

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source harv_venv/bin/activate

# Install backend dependencies
echo "📚 Installing backend dependencies..."
cd backend
pip install -q -r requirements.txt

# Create .env file with API key
echo "🔧 Setting up environment..."
echo "OPENAI_API_KEY=$OPENAI_KEY" > .env
echo "JWT_SECRET_KEY=$(openssl rand -hex 32)" >> .env

# Go back to root
cd ..

# Install frontend dependencies
echo "⚛️  Installing frontend dependencies..."
cd frontend
npm install --legacy-peer-deps --silent

# Go back to root
cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Starting HARV platform..."
echo "================================"

# Start backend in background
echo "🔧 Starting backend server..."
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Start frontend
echo "⚛️  Starting frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
sleep 3

echo ""
echo "🎉 HARV Platform is running!"
echo "============================"
echo ""
echo "🌐 Frontend: http://localhost:5173"
echo "🔧 Backend:  http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo ""
echo "📚 Default test account:"
echo "   Email: test@example.com"
echo "   Password: testpass123"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping HARV services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

# Set up signal handler
trap cleanup SIGINT SIGTERM

# Keep script running
wait