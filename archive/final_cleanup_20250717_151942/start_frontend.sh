#!/bin/bash
# Harv Frontend Startup Script

echo "🌱 Starting Harv Frontend..."
echo "============================"

# Navigate to frontend directory
cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start development server
echo "🚀 Starting React development server..."
echo "Frontend will be available at: http://localhost:5173"
echo "Backend should be running at: http://127.0.0.1:8000"
echo ""
echo "Press Ctrl+C to stop the server"

npm run dev
