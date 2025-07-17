# 🌱 Harv - Complete AI-Powered Socratic Learning Platform

A sophisticated educational platform that uses Socratic questioning to guide students through mass communication concepts.

## 🚀 Quick Start

### One-Command Launch
```bash
bash start_complete_platform.sh
```

### Manual Launch
```bash
# Terminal 1 - Backend
bash start_backend.sh

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

## 🎯 What You Get

### Complete Platform Features
- **Landing Page**: Beautiful authentication with form validation
- **Dashboard**: Module selection with progress tracking
- **Chat Interface**: Real-time Socratic tutoring with AI
- **Memory System**: Context-aware conversations
- **Export System**: Download conversations for study
- **Responsive Design**: Works on all devices

### Technical Excellence
- **Frontend**: React 18 + Vite + Tailwind CSS
- **Backend**: Python FastAPI with SQLite
- **Authentication**: JWT tokens with protected routes
- **AI Integration**: OpenAI GPT for Socratic questioning
- **State Management**: React Context
- **API Design**: RESTful endpoints

## 🏗️ Architecture

```
harv/
├── frontend/              # React application
│   ├── src/
│   │   ├── pages/         # Landing, Dashboard, Module pages
│   │   ├── components/    # Reusable UI components
│   │   ├── services/      # API integration
│   │   └── context/       # Authentication state
├── backend/               # Python FastAPI backend
│   └── app/               # Your existing backend code
├── start_backend.sh       # Backend startup script
├── start_complete_platform.sh  # Complete platform launcher
└── README.md             # This file
```

## 🌐 URLs

- **Frontend**: http://localhost:5173
- **Backend**: http://127.0.0.1:8000  
- **API Docs**: http://127.0.0.1:8000/docs

## ⚙️ Configuration

### Backend Setup
1. Add your OpenAI API key to `backend/.env`:
   ```
   OPENAI_API_KEY=sk-your-actual-api-key
   ```

2. Your backend should have these endpoints:
   - `GET /health` - Health check
   - `GET /modules` - List all modules
   - `POST /auth/register` - User registration
   - `POST /auth/login` - User authentication
   - `POST /chat/` - AI conversation

### Frontend Configuration
The frontend automatically connects to your backend. Environment variables in `frontend/.env`:
```
VITE_API_URL=http://127.0.0.1:8000
```

## 🧪 Testing Your Platform

1. **Start platform**: `bash start_complete_platform.sh`
2. **Visit frontend**: http://localhost:5173
3. **Create account**: Register with email/password
4. **Browse modules**: See your 15 communication modules
5. **Start chatting**: Click any module to chat with Harv
6. **Test Socratic method**: Ask questions and explore concepts
7. **Export conversations**: Download your learning sessions

## 🔧 Troubleshooting

### Backend Issues
```bash
# Check if backend is running
curl http://127.0.0.1:8000/health

# View backend logs
bash start_backend.sh

# Install missing dependencies
cd backend
source venv/bin/activate  # or .venv/bin/activate
pip install fastapi uvicorn sqlalchemy python-jose bcrypt python-multipart openai
```

### Frontend Issues
```bash
# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install

# Check if frontend is accessible
curl http://localhost:5173
```

### Common Fixes
- **CORS errors**: Backend CORS is configured for localhost:5173
- **API connection**: Make sure backend is running first
- **OpenAI errors**: Add valid API key to backend/.env
- **Module loading**: Backend must return array of modules

## 📁 Project Structure

### Frontend (`frontend/`)
```
src/
├── pages/
│   ├── LandingPage.jsx    # Authentication & hero
│   ├── Dashboard.jsx      # Module selection
│   └── ModulePage.jsx     # Chat interface
├── components/
│   ├── layout/Header.jsx  # Navigation header
│   └── auth/ProtectedRoute.jsx  # Route protection
├── services/api.js        # Backend integration
├── context/AuthContext.jsx  # Authentication state
└── index.css             # Global styles
```

### Backend Integration
The frontend expects these API responses:

**Authentication**:
```json
{
  "access_token": "jwt-token",
  "token_type": "bearer",
  "user": { "email": "user@example.com" }
}
```

**Modules**:
```json
[
  {
    "id": 1,
    "title": "Communication Theory",
    "description": "Explore fundamental concepts..."
  }
]
```

**Chat**:
```json
{
  "reply": "That's interesting! What led you to think about it that way?",
  "conversation_id": "uuid",
  "module_id": 1
}
```

## 🎓 Socratic Learning Flow

1. **Student asks question** → System processes with memory context
2. **AI responds with question** → Guides discovery vs giving answers  
3. **Conversation builds** → Memory system tracks learning progression
4. **Export available** → Students can download for review

## 🚢 Production Deployment

### Environment Variables
```bash
# Backend (.env)
OPENAI_API_KEY=sk-your-actual-key
JWT_SECRET_KEY=super-secret-production-key
DATABASE_URL=postgresql://user:pass@host:port/db

# Frontend (.env)
VITE_API_URL=https://your-backend-domain.com
```

### Build Commands
```bash
# Frontend production build
cd frontend
npm run build

# Backend production
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📊 Features Implemented

✅ **Complete Authentication System**
- Registration with validation
- Login with JWT tokens
- Protected routes
- User context management

✅ **Module Management**
- Dynamic module loading from backend
- Module cards with descriptions
- Click-to-start functionality
- Loading states and error handling

✅ **AI Chat Interface**  
- Real-time messaging
- Socratic question responses
- Message history
- Typing indicators
- Export functionality

✅ **Professional UI/UX**
- Responsive design (mobile-first)
- Tailwind CSS styling
- Loading spinners
- Error states
- Smooth animations

✅ **Backend Integration**
- RESTful API communication
- Error handling with fallbacks
- Health checking
- Memory system integration

## 🛠️ Built With

- **React 18** - Modern UI framework
- **Vite** - Fast build tool
- **Tailwind CSS** - Utility-first styling
- **React Router** - Client-side routing
- **Lucide React** - Beautiful icons
- **FastAPI** - Python backend framework
- **OpenAI API** - AI conversation engine

## 📈 Next Steps

After getting the platform running:

1. **Customize modules** - Add your specific course content
2. **Enhance memory system** - Fine-tune learning context
3. **Add analytics** - Track student progress
4. **Deploy to production** - Host on cloud platform
5. **Scale for more users** - Optimize for larger cohorts

---

**Built for the Harv Platform - AI-Powered Socratic Learning** 🌱

For support, check that your backend endpoints match the expected API format above.
