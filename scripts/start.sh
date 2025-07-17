#!/bin/bash
# Fixed Start Script - Actually works
# Run from harv root directory: bash scripts/start.sh

echo "🚀 Starting Harv Platform..."

# Check if virtual environment exists
if [ ! -d "harv_venv" ]; then
    echo "❌ Virtual environment not found. Run: bash scripts/setup.sh"
    exit 1
fi

# Activate virtual environment
source harv_venv/bin/activate

# Kill any existing processes first
echo "🧹 Stopping any existing services..."
pkill -f "uvicorn app.main:app" 2>/dev/null
pkill -f "python3 -m http.server 3000" 2>/dev/null
pkill -f "vite" 2>/dev/null

sleep 2

# Start backend
echo "🔧 Starting backend..."
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Check if dev-gui.html exists, create if missing
if [ ! -f "tools/dev-gui.html" ]; then
    echo "📝 Creating GUI file..."
    mkdir -p tools
    cat > tools/dev-gui.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Harv Configuration GUI</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 2rem; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 2rem; border-radius: 8px; }
        h1 { color: #3E5641; }
        .status { padding: 1rem; background: #e8f4f0; border-radius: 4px; margin-bottom: 1rem; }
        .links { display: flex; gap: 1rem; margin-top: 2rem; }
        .link { padding: 0.75rem 1.5rem; background: #3E5641; color: white; text-decoration: none; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌱 Harv Platform Configuration</h1>
        <div class="status">
            <strong>Platform Status:</strong> Running
        </div>
        <p>Your Harv AI platform is running successfully!</p>
        
        <h3>Access Points:</h3>
        <ul>
            <li><strong>Frontend:</strong> <a href="http://localhost:5173">http://localhost:5173</a></li>
            <li><strong>Backend API:</strong> <a href="http://localhost:8000">http://localhost:8000</a></li>
            <li><strong>API Docs:</strong> <a href="http://localhost:8000/docs">http://localhost:8000/docs</a></li>
        </ul>
        
        <div class="links">
            <a href="http://localhost:5173" class="link">Open Frontend</a>
            <a href="http://localhost:8000/docs" class="link">API Documentation</a>
        </div>
        
        <h3>Quick Tests:</h3>
        <ul>
            <li><a href="http://localhost:8000/health">Backend Health Check</a></li>
            <li><a href="http://localhost:8000/modules">View All Modules</a></li>
        </ul>
    </div>
</body>
</html>
EOF
fi

# Start GUI server on port 3001 (to avoid conflict)
echo "🎨 Starting configuration GUI..."
cd tools
python3 -m http.server 3001 &
GUI_PID=$!
cd ..

# Start frontend
echo "⚛️  Starting React frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

sleep 2

echo ""
echo "🎉 Harv Platform Started Successfully!"
echo "====================================="
echo "🔧 Backend:       http://localhost:8000"
echo "🎨 GUI:           http://localhost:3001/dev-gui.html"  
echo "⚛️  Frontend:     http://localhost:5173"
echo "📖 API Docs:     http://localhost:8000/docs"
echo ""
echo "✅ All services running!"
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping all services..."
    kill $BACKEND_PID 2>/dev/null
    kill $GUI_PID 2>/dev/null  
    kill $FRONTEND_PID 2>/dev/null
    pkill -f "uvicorn app.main:app" 2>/dev/null
    pkill -f "python3 -m http.server 3001" 2>/dev/null
    pkill -f "vite" 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait
