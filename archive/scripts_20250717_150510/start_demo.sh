#!/bin/bash
# Start Demo Mode - Test Your Configured Modules
echo "🎮 STARTING HARV DEMO MODE"
echo "=========================="

# Check if backend is running
echo "🔍 Checking backend..."
if curl -s http://127.0.0.1:8000/health > /dev/null; then
    echo "✅ Backend is running"
else
    echo "⚠️  Backend not detected - starting it..."
    cd backend
    uvicorn app.main:app --reload &
    BACKEND_PID=$!
    cd ..
    echo "✅ Backend started (PID: $BACKEND_PID)"
    sleep 3
fi

# Check if GUI is running
echo "🔍 Checking GUI..."
if curl -s http://localhost:3000/dev-gui.html > /dev/null; then
    echo "✅ GUI is running"
else
    echo "⚠️  GUI not detected - starting it..."
    cd tools
    python3 -m http.server 3000 &
    GUI_PID=$!
    cd ..
    echo "✅ GUI started (PID: $GUI_PID)"
    sleep 2
fi

# Start demo frontend
echo "🚀 Starting demo frontend..."
cd demo_frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

echo ""
echo "🎉 DEMO MODE READY!"
echo "==================="
echo ""
echo "🔧 Configure: http://localhost:3000/dev-gui.html"
echo "🎮 Test: http://localhost:3000 (will open automatically)"
echo ""
echo "Workflow:"
echo "1. Configure memory/prompts in GUI"
echo "2. Save configuration"
echo "3. Test immediately in demo"
echo "4. See AI responses using your config"
echo ""

# Start React app (will open browser automatically)
npm start
