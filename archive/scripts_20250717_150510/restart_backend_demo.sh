#!/bin/bash
# Restart Backend and Demo
echo "🔄 Restarting Backend and Demo..."

# Kill existing backend processes
pkill -f "uvicorn app.main:app"

# Start backend with updated CORS
echo "🚀 Starting backend with updated CORS..."
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"

# Wait for backend to start
sleep 3

# Test backend
if curl -s http://127.0.0.1:8000/health > /dev/null; then
    echo "✅ Backend health check passed"
else
    echo "❌ Backend health check failed"
fi

echo ""
echo "🎯 Demo should now show '✅ Backend Connected'"
echo "   Demo URL: http://localhost:3001"
echo "   Backend:  http://127.0.0.1:8000"
echo ""
echo "💡 If demo still shows 'Backend Not Connected':"
echo "   - Force refresh: Ctrl+F5 (or Cmd+Shift+R)"
echo "   - Check browser console (F12) for errors"
