#!/bin/bash
# Complete Harv Platform Startup - Starts Everything

echo "🌱 STARTING COMPLETE HARV PLATFORM"
echo "==================================="

# Function to check if port is in use
check_port() {
    lsof -i :$1 > /dev/null 2>&1
}

# Function to wait for service
wait_for_service() {
    local url=$1
    local name=$2
    echo "⏳ Waiting for $name to start..."
    for i in {1..30}; do
        if curl -s $url > /dev/null 2>&1; then
            echo "✅ $name is ready!"
            return 0
        fi
        sleep 1
    done
    echo "⚠️  $name may not be responding"
    return 1
}

# Start backend if not running
if ! check_port 8000; then
    echo "🐍 Starting Python backend..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        osascript -e 'tell application "Terminal" to do script "cd '$(pwd)' && bash start_backend.sh"'
    else
        # Linux/Windows
        gnome-terminal -- bash -c "cd $(pwd) && bash start_backend.sh; exec bash" 2>/dev/null || \
        xterm -e "cd $(pwd) && bash start_backend.sh" 2>/dev/null || \
        bash start_backend.sh &
    fi
    wait_for_service "http://127.0.0.1:8000/health" "Backend"
else
    echo "✅ Backend already running on port 8000"
fi

# Start frontend if not running
if ! check_port 5173; then
    echo "⚛️ Starting React frontend..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        osascript -e 'tell application "Terminal" to do script "cd '$(pwd)'/frontend && npm run dev"'
    else
        # Linux/Windows
        gnome-terminal -- bash -c "cd $(pwd)/frontend && npm run dev; exec bash" 2>/dev/null || \
        xterm -e "cd $(pwd)/frontend && npm run dev" 2>/dev/null || \
        (cd frontend && npm run dev) &
    fi
    wait_for_service "http://localhost:5173" "Frontend"
else
    echo "✅ Frontend already running on port 5173"
fi

echo ""
echo "🎉 HARV PLATFORM STARTED!"
echo "========================="
echo "🌐 Frontend: http://localhost:5173"
echo "🔧 Backend:  http://127.0.0.1:8000"
echo "📚 API Docs: http://127.0.0.1:8000/docs"
echo ""
echo "🚀 Ready to use your AI-powered Socratic learning platform!"
echo ""
echo "📋 Next steps:"
echo "1. Visit http://localhost:5173"
echo "2. Create an account or login"
echo "3. Choose a module to start learning"
echo "4. Chat with Harv using Socratic questioning"
echo ""
echo "💡 Tip: Make sure you've added your OpenAI API key to backend/.env"
