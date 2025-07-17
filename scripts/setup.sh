#!/bin/bash
# Harv Platform Setup
echo "🌱 Setting up Harv Platform..."

# Create virtual environment if it doesn't exist
if [ ! -d "harv_venv" ]; then
    python3 -m venv harv_venv
    echo "✅ Created virtual environment"
fi

# Activate virtual environment
source harv_venv/bin/activate

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
pip install -q fastapi uvicorn sqlalchemy pydantic passlib[bcrypt] python-jose[cryptography] python-multipart openai python-dotenv
cd ..

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Create .env file if it doesn't exist
if [ ! -f "backend/.env" ]; then
    echo "📝 Creating .env template..."
    cat > backend/.env << 'ENVEOF'
# Add your OpenAI API key here
OPENAI_API_KEY=your_openai_key_here

# JWT Secret (auto-generated)
JWT_SECRET_KEY=harv_secret_key_change_in_production

# Database
DATABASE_URL=sqlite:///./harv.db
ENVEOF
    echo "⚠️  Please add your OpenAI API key to backend/.env"
fi

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Add your OpenAI API key to backend/.env"
echo "2. Run: bash scripts/start.sh"
