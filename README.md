# 🌱 HARV - AI-Powered Socratic Learning Platform

**HARV** (Holistic AI Resource for Virtual education) is a sophisticated educational platform that uses AI-powered Socratic questioning to guide students through mass communication concepts. Instead of providing direct answers, HARV asks strategic questions that lead students to discover knowledge themselves.

## 🎯 Key Features

- **Socratic AI Tutoring**: Guides learning through strategic questioning
- **4-Layer Memory System**: Maintains context across conversations
- **15 Communication Modules**: Complete mass communication curriculum
- **JWT Authentication**: Secure user sessions
- **Progress Tracking**: Monitor learning journey
- **Export Capabilities**: Download conversations for study

## 📋 Prerequisites

Before you begin, ensure you have:
- Python 3.8+ installed
- Node.js 18+ and npm installed
- OpenAI API key (GPT-4 access recommended)
- SQLite3 (usually pre-installed)
- 2GB free disk space

## 🚀 Quick Start (5 Minutes)

### 1. Clone and Setup Environment

```bash
# Clone the repository
git clone [repository-url]
cd harv

# Create Python virtual environment
python3 -m venv harv_venv
source harv_venv/bin/activate  # On Windows: harv_venv\Scripts\activate

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install --legacy-peer-deps
cd ..
```

### 2. Configure OpenAI API Key

```bash
# Create backend environment file
echo "OPENAI_API_KEY=your-openai-api-key-here" > backend/.env
```

Replace `your-openai-api-key-here` with your actual OpenAI API key.

### 3. Start the Platform

```bash
# From the harv root directory
bash scripts/start.sh
```

This starts:
- Backend API on http://localhost:8000
- Frontend on http://localhost:5173
- Developer GUI on http://localhost:3001

### 4. Access the Platform

Open your browser and go to: **http://localhost:5173**

## 📖 Detailed Setup Instructions

### Backend Setup (FastAPI + SQLite)

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install fastapi uvicorn sqlalchemy python-jose bcrypt python-multipart openai python-dotenv
   # OR
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create `.env` file in backend directory:
   ```env
   OPENAI_API_KEY=sk-proj-your-actual-api-key
   JWT_SECRET_KEY=your-secret-key-min-32-chars
   DATABASE_URL=sqlite:///./harv.db
   ```

5. **Start backend server**:
   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

### Frontend Setup (React + Vite)

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install --legacy-peer-deps
   ```

3. **Configure API endpoint** (optional):
   Edit `frontend/.env`:
   ```env
   VITE_API_URL=http://localhost:8000
   ```

4. **Start development server**:
   ```bash
   npm run dev
   ```

## 👤 Using HARV Platform

### 1. Create an Account

1. Go to http://localhost:5173
2. Click "Get Started" or "Sign Up"
3. Fill in:
   - **Email**: Your email address
   - **Password**: Minimum 6 characters
   - **Name**: Your full name
   - **Learning Goals**: What you hope to learn
   - **Background**: Your experience level

### 2. Login

Use your registered email and password to login.

### 3. Select a Module

Choose from 15 communication modules:
- Module 1: Your Four Worlds
- Module 2: Media Uses & Effects
- Module 3: Shared Characteristics of Media
- Module 4: Communication Infrastructure
- Module 5: Books: The Birth of Mass Communication
- Module 6: News & Newspapers
- Module 7: Magazines: The Special Interest Medium
- Module 8: Comic Books: Small Business, Big Impact
- Module 9: Photography: Fixing a Shadow
- Module 10: Recordings: From Bach to Rock & Rap
- Module 11: Motion Pictures: The Start of Mass Entertainment
- Module 12: Radio: The Pervasive Medium
- Module 13: Television: The Center of Attention
- Module 14: Video Games: The Newest Mass Medium
- Module 15: Economic Influencers: Advertising, PR, and Ownership

### 4. Start Learning with Socratic AI

1. Click on any module to start
2. Ask questions about the topic
3. HARV will respond with guiding questions
4. Think through the questions and respond
5. Continue the dialogue to deepen understanding

**Example Conversation**:
```
You: "What is mass communication?"

HARV: "Great question! To really understand mass communication, 
consider this: What features distinguish mass communication from 
other forms of communication? And why do you think these 
attributes are crucial to its definition?"

You: "Well, it reaches many people at once..."

HARV: "Indeed! Let's delve deeper - why do you think it's 
potentially advantageous for information to reach many people 
at once? And how might the lack of personalization impact 
the interpretation?"
```

### 5. Export Your Learning

Click "Export Conversation" to download your chat history for:
- Study notes
- Assignment submission
- Personal review

## 💻 Using HARV CLI

The CLI provides direct access to HARV's functionality:

```bash
# Start the CLI
python harv_cli.py

# Main Menu Options:
1. 🎓 New Student Profile - Create a new learning profile
2. 👤 Existing Student - Continue with existing profile
3. 🌐 Connect to Backend - Use with running backend
4. 📖 Getting Started - View help
5. 🚪 Exit
```

### CLI Features:
- **Offline Mode**: Works without backend server
- **Module Selection**: Access all 15 modules
- **Conversation History**: Saves all dialogues
- **Progress Tracking**: Monitor completion
- **Export Options**: JSON, TXT, or MD formats

## 🔧 API Endpoints

### Authentication
- `POST /auth/register` - Create new account
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user
- `POST /auth/logout` - Logout

### Modules
- `GET /modules` - List all modules
- `GET /modules/{id}` - Get specific module
- `GET /modules/{id}/config` - Get module configuration

### Chat
- `POST /chat/` - Send message (basic)
- `POST /chat/enhanced` - Send message (with memory)
- `GET /memory/{user_id}/{module_id}` - Get memory context

### Health
- `GET /health` - System health check
- `GET /` - API information

## 📊 Testing the System

### 1. Test Backend Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "enhanced_memory": true,
  "openai_configured": true
}
```

### 2. Test User Registration
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "name": "Test User"
  }'
```

### 3. Test Chat Functionality
```bash
# First login to get token
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' \
  | jq -r '.access_token')

# Send chat message
curl -X POST http://localhost:8000/chat/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is communication theory?",
    "module_id": 1,
    "user_id": 1
  }'
```

## 🐛 Troubleshooting

### Backend Issues

**Problem**: "Address already in use"
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

**Problem**: "OpenAI API error"
- Check your API key in `backend/.env`
- Ensure you have GPT-4 access
- Check OpenAI API status

**Problem**: "Database error"
```bash
# Reset database
cd backend
rm harv.db
python -c "from app.main import Base, engine; Base.metadata.create_all(bind=engine)"
```

### Frontend Issues

**Problem**: "npm install fails"
```bash
# Use legacy peer deps
npm install --legacy-peer-deps
```

**Problem**: "Vite not found"
```bash
# Install vite explicitly
npm install vite --save-dev
```

**Problem**: "CORS errors"
- Ensure backend is running on port 8000
- Check frontend is using correct API URL

## 🔒 Security Considerations

1. **API Keys**: Never commit `.env` files
2. **JWT Tokens**: Expire after 24 hours
3. **Passwords**: Bcrypt hashed in database
4. **CORS**: Configured for localhost only
5. **SQL Injection**: Protected by SQLAlchemy ORM

## 📁 Project Structure

```
harv/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI application
│   │   ├── models.py         # Database models
│   │   ├── auth.py           # Authentication logic
│   │   ├── database.py       # Database connection
│   │   └── endpoints/        # API endpoints
│   ├── harv.db              # SQLite database
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── pages/           # React pages
│   │   ├── components/      # UI components
│   │   ├── services/        # API calls
│   │   └── context/         # State management
│   ├── package.json         # Node dependencies
│   └── vite.config.js       # Vite configuration
├── scripts/
│   ├── start.sh            # Start all services
│   └── setup.sh            # Initial setup
├── harv_cli.py             # Command-line interface
└── README.md               # This file
```

## 🚀 Production Deployment

### 1. Environment Variables
```bash
# Production .env
OPENAI_API_KEY=sk-prod-key
JWT_SECRET_KEY=production-secret-min-32-chars
DATABASE_URL=postgresql://user:pass@host/db
```

### 2. Build Frontend
```bash
cd frontend
npm run build
# Deploy dist/ folder to CDN or static host
```

### 3. Deploy Backend
```bash
# Using Docker
docker build -t harv-backend ./backend
docker run -p 8000:8000 harv-backend

# Using PM2
pm2 start "uvicorn app.main:app" --name harv-backend
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push branch (`git push origin feature/amazing`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

- **Documentation**: See `/docs` folder
- **Issues**: GitHub Issues
- **Email**: support@harv-education.com

---

**Happy Learning with HARV!** 🌱📚

*Remember: The best learning happens through discovery, not memorization.*