#!/bin/bash
# Start Harv Platform - Complete System
echo "🚀 Starting Harv Platform..."

# Check if virtual environment exists
if [ ! -d "harv_venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv harv_venv
fi

# Activate virtual environment
source harv_venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q fastapi uvicorn sqlalchemy passlib[bcrypt] pydantic openai python-dotenv

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file..."
    cat > .env << 'ENVEOF'
OPENAI_API_KEY=your-openai-key-here
JWT_SECRET_KEY=your-secure-jwt-secret-here
DATABASE_URL=sqlite:///./harv.db
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
ENVEOF
fi

# Start backend
echo "🔧 Starting backend..."
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start GUI
echo "🎨 Starting GUI..."
cd ../tools
python3 -m http.server 3000 &
GUI_PID=$!

echo ""
echo "🎉 Harv Platform is running!"
echo "Backend: http://localhost:8000"
echo "GUI: http://localhost:3000/dev-gui.html"
echo "Health: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for interrupt
trap "kill $BACKEND_PID $GUI_PID 2>/dev/null; exit" INT
wait
