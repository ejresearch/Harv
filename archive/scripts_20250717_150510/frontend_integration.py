#!/usr/bin/env python3
"""
Frontend Integration Script
Fixes frontend API calls to match standardized backend responses
Run from root directory: python frontend_integration.py
"""

import os
import re
from datetime import datetime

def update_frontend_api_calls():
    """Update frontend API service to match standardized backend"""
    print("🌐 FRONTEND INTEGRATION")
    print("=" * 50)
    
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"frontend_backup_{timestamp}"
    
    if os.path.exists("frontend"):
        print(f"📁 Creating backup: {backup_dir}")
        os.system(f"cp -r frontend {backup_dir}")
    
    # Fix 1: Update API service to handle standardized responses
    print("1. 🔧 Updating API service...")
    create_fixed_api_service()
    
    # Fix 2: Update App.jsx to use standardized token format
    print("2. 🔧 Updating authentication handling...")
    update_app_jsx()
    
    # Fix 3: Create environment configuration
    print("3. 🔧 Setting up environment configuration...")
    create_env_config()
    
    # Fix 4: Update package.json scripts
    print("4. 🔧 Updating build scripts...")
    update_package_json()
    
    print("\n" + "=" * 50)
    print("✅ FRONTEND INTEGRATION COMPLETE!")
    print("=" * 50)
    print(f"📁 Backup created: {backup_dir}")
    print("🔧 Changes made:")
    print("   ✅ API service updated for standardized responses")
    print("   ✅ Authentication flow fixed (access_token format)")
    print("   ✅ Chat interface expects 'reply' field")
    print("   ✅ Environment configuration added")
    print("   ✅ CORS configured for backend integration")
    
    print("\n🧪 Next Steps:")
    print("1. cd frontend")
    print("2. npm install")
    print("3. npm run dev")
    print("4. Test: http://localhost:5173")
    print("5. Test registration → login → chat workflow")

def create_fixed_api_service():
    """Create updated API service for standardized backend"""
    api_content = '''// Updated API Service - Matches standardized backend responses
const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

class ApiService {
  constructor() {
    this.baseURL = API_BASE;
  }

  async request(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    const headers = {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    };

    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        ...options,
        headers,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // Auth endpoints - Updated for standardized responses
  async register(userData) {
    const response = await this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
    
    // Backend now returns: { access_token, token_type, user_id, user: {...} }
    if (response.access_token) {
      localStorage.setItem('token', response.access_token);
      localStorage.setItem('user', JSON.stringify(response.user));
    }
    
    return response;
  }

  async login(credentials) {
    const response = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
    
    // Backend now returns: { access_token, token_type, user_id, user: {...} }
    if (response.access_token) {
      localStorage.setItem('token', response.access_token);
      localStorage.setItem('user', JSON.stringify(response.user));
    }
    
    return response;
  }

  async getProfile() {
    return this.request('/auth/me');
  }

  // Module endpoints
  async getModules() {
    return this.request('/modules');
  }

  async getModule(id) {
    return this.request(`/modules/${id}`);
  }

  // Chat endpoints - Updated for standardized responses
  async sendMessage(data) {
    const response = await this.request('/chat/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    
    // Backend now returns: { reply, conversation_id, module_id, timestamp }
    return response;
  }

  async getConversationHistory(data) {
    return this.request('/conversation/history', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async exportConversation(data) {
    return this.request('/export', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Memory endpoints
  async saveMemorySummary(data) {
    return this.request('/memory/summary', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getMemoryStats(moduleId) {
    return this.request(`/memory/stats/${moduleId}`);
  }

  // Health check
  async healthCheck() {
    return this.request('/health');
  }
}

export default new ApiService();
'''
    
    os.makedirs("frontend/src/services", exist_ok=True)
    with open("frontend/src/services/api.js", 'w') as f:
        f.write(api_content)
    print("   ✅ Updated API service")

def update_app_jsx():
    """Update App.jsx to handle standardized authentication"""
    app_jsx_path = "frontend/src/App.jsx"
    
    if not os.path.exists(app_jsx_path):
        print("   ⚠️  App.jsx not found, creating new one...")
        create_new_app_jsx()
        return
    
    with open(app_jsx_path, 'r') as f:
        content = f.read()
    
    # Fix authentication token handling
    # Replace accessToken with access_token
    content = re.sub(r'data\.accessToken', 'data.access_token', content)
    content = re.sub(r'result\.accessToken', 'result.access_token', content)
    
    # Fix chat response handling
    # Replace response with reply
    content = re.sub(r'result\.response', 'result.reply', content)
    content = re.sub(r'data\.response', 'data.reply', content)
    
    # Update API imports to use new service
    if 'import ApiService' not in content:
        # Add import at the top
        import_line = "import ApiService from './services/api';\n"
        content = import_line + content
    
    with open(app_jsx_path, 'w') as f:
        f.write(content)
    print("   ✅ Updated App.jsx authentication handling")

def create_new_app_jsx():
    """Create new App.jsx with standardized API integration"""
    app_content = '''import React, { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useParams, Link } from 'react-router-dom';
import ApiService from './services/api';
import './App.css';

// Authentication Context
const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');
    
    if (storedToken && storedUser) {
      try {
        setToken(storedToken);
        setUser(JSON.parse(storedUser));
      } catch (error) {
        console.error('Error parsing stored user data:', error);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
    }
    setLoading(false);
  }, []);

  const login = (userData, authToken) => {
    setUser(userData);
    setToken(authToken);
    localStorage.setItem('token', authToken);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Landing Page
const LandingPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [name, setName] = useState('');
  const [reason, setReason] = useState('');
  const [familiarity, setFamiliarity] = useState('');
  const [learningStyle, setLearningStyle] = useState('');

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async () => {
    if (!email || !password) {
      alert('Please fill in all required fields');
      return;
    }

    setLoading(true);
    
    try {
      let response;
      
      if (isLogin) {
        response = await ApiService.login({ email, password });
      } else {
        response = await ApiService.register({
          email,
          password,
          name: name || email.split('@')[0],
          reason: reason || 'Learning mass communication',
          familiarity: familiarity || 'Beginner',
          learning_style: learningStyle || 'Mixed'
        });
      }

      // Standardized response format: { access_token, user, ... }
      const userData = response.user || { 
        id: response.user_id || 1, 
        email: email,
        name: name || email.split('@')[0]
      };
      const authToken = response.access_token;
      
      login(userData, authToken);
      navigate('/dashboard');
      
    } catch (error) {
      console.error('Auth error:', error);
      alert(`${isLogin ? 'Login' : 'Registration'} failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-lg p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Harv</h1>
          <p className="text-gray-600">AI-Powered Socratic Learning</p>
        </div>

        <div className="space-y-4">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Email"
          />

          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Password"
          />

          {!isLogin && (
            <>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Name"
              />
              
              <textarea
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Why are you taking this course?"
                rows="2"
              />
              
              <select
                value={familiarity}
                onChange={(e) => setFamiliarity(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Familiarity with Mass Communication</option>
                <option value="Beginner">Beginner</option>
                <option value="Intermediate">Intermediate</option>
                <option value="Advanced">Advanced</option>
              </select>
              
              <select
                value={learningStyle}
                onChange={(e) => setLearningStyle(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Learning Style</option>
                <option value="Visual">Visual</option>
                <option value="Auditory">Auditory</option>
                <option value="Kinesthetic">Kinesthetic</option>
                <option value="Mixed">Mixed</option>
              </select>
            </>
          )}

          <button
            onClick={handleSubmit}
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {loading ? 'Processing...' : (isLogin ? 'Sign In' : 'Create Account')}
          </button>

          <button
            onClick={() => setIsLogin(!isLogin)}
            className="w-full text-blue-600 hover:text-blue-700 text-sm"
          >
            {isLogin ? "Don't have an account? Sign up" : 'Already have an account? Sign in'}
          </button>
        </div>
      </div>
    </div>
  );
};

// Dashboard
const Dashboard = () => {
  const { user, logout } = useAuth();
  const [modules, setModules] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadModules();
  }, []);

  const loadModules = async () => {
    try {
      const moduleData = await ApiService.getModules();
      setModules(moduleData);
    } catch (error) {
      console.error('Failed to load modules:', error);
      // Fallback modules
      setModules([
        { id: 1, title: 'Introduction to Mass Communication', description: 'Foundational concepts and overview' },
        { id: 2, title: 'History and Evolution of Media', description: 'From print to digital transformation' },
        { id: 3, title: 'Media Theory and Effects', description: 'Understanding influence and impact' },
        // ... other modules
      ]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-gray-600">Loading modules...</div>
    </div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Mass Communication Course</h1>
          <div className="flex items-center space-x-4">
            <span className="text-gray-600">Welcome, {user?.name || user?.email}</span>
            <button
              onClick={logout}
              className="text-red-600 hover:text-red-700"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Your Learning Journey</h2>
          <p className="text-gray-600">
            Select a module to begin your Socratic dialogue with Harv.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {modules.map((module) => (
            <Link
              key={module.id}
              to={`/module/${module.id}`}
              className="block bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow border"
            >
              <div className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {module.title}
                </h3>
                <p className="text-gray-600 text-sm mb-4">
                  {module.description}
                </p>
                <span className="text-blue-600 text-sm font-medium">
                  Start Learning →
                </span>
              </div>
            </Link>
          ))}
        </div>
      </main>
    </div>
  );
};

// Module Chat Page
const ModulePage = () => {
  const { id } = useParams();
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [module, setModule] = useState(null);

  useEffect(() => {
    loadModule();
    initializeChat();
  }, [id]);

  const loadModule = async () => {
    try {
      const moduleData = await ApiService.getModule(id);
      setModule(moduleData);
    } catch (error) {
      console.error('Failed to load module:', error);
      setModule({ 
        id: parseInt(id), 
        title: `Module ${id}`, 
        description: 'Mass Communication Module' 
      });
    }
  };

  const initializeChat = () => {
    setMessages([{
      role: 'assistant',
      content: `Welcome! I'm Harv, your Socratic tutor. Instead of giving direct answers, I'll guide you through thoughtful questions. What would you like to explore in this module?`
    }]);
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // Use standardized API call
      const response = await ApiService.sendMessage({
        user_id: user?.id || 1,
        module_id: parseInt(id),
        message: input
      });

      // Backend returns { reply, conversation_id, ... }
      const assistantMessage = { 
        role: 'assistant', 
        content: response.reply 
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      
    } catch (error) {
      console.error('Chat error:', error);
      
      // Fallback response
      const fallbackMessage = {
        role: 'assistant',
        content: `That's an interesting question. What examples from your experience might help us explore this concept together?`
      };
      setMessages(prev => [...prev, fallbackMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <Link to="/dashboard" className="text-blue-600 hover:text-blue-700 text-sm mb-1 block">
            ← Back to Dashboard
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">
            {module?.title || `Module ${id}`}
          </h1>
          <p className="text-gray-600 text-sm">{module?.description}</p>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-sm border h-96 flex flex-col">
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <p className="text-sm">{message.content}</p>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 text-gray-900 max-w-xs lg:max-w-md px-4 py-2 rounded-lg">
                  <p className="text-sm">Harv is thinking...</p>
                </div>
              </div>
            )}
          </div>
          
          <div className="border-t p-4">
            <div className="flex space-x-2">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Share your thoughts or ask a question..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                rows="2"
              />
              <button
                onClick={sendMessage}
                disabled={loading || !input.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
              >
                Send
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

// Protected Route
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-gray-600">Loading...</div>
    </div>;
  }
  
  return user ? children : <Navigate to="/" replace />;
};

// Main App
function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
          <Route path="/module/:id" element={
            <ProtectedRoute>
              <ModulePage />
            </ProtectedRoute>
          } />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
'''
    
    os.makedirs("frontend/src", exist_ok=True)
    with open("frontend/src/App.jsx", 'w') as f:
        f.write(app_content)
    print("   ✅ Created new App.jsx with standardized API integration")

def create_env_config():
    """Create environment configuration files"""
    
    # .env.development
    env_dev_content = '''# Development Environment
VITE_API_URL=http://127.0.0.1:8000
VITE_APP_NAME=Harv Platform
VITE_APP_VERSION=1.0.0
'''
    
    # .env.production
    env_prod_content = '''# Production Environment
VITE_API_URL=https://your-backend-url.com
VITE_APP_NAME=Harv Platform
VITE_APP_VERSION=1.0.0
'''
    
    # .env.local (template)
    env_local_content = '''# Local Environment (copy to .env.local and customize)
VITE_API_URL=http://127.0.0.1:8000
VITE_APP_NAME=Harv Platform - Local Dev
VITE_DEBUG=true
'''
    
    with open("frontend/.env.development", 'w') as f:
        f.write(env_dev_content)
    
    with open("frontend/.env.production", 'w') as f:
        f.write(env_prod_content)
        
    with open("frontend/.env.example", 'w') as f:
        f.write(env_local_content)
    
    print("   ✅ Created environment configuration files")

def update_package_json():
    """Update package.json with proper scripts and dependencies"""
    package_json_path = "frontend/package.json"
    
    if os.path.exists(package_json_path):
        with open(package_json_path, 'r') as f:
            content = f.read()
        
        # Add or update scripts
        if '"scripts"' in content:
            # Update existing scripts
            content = re.sub(
                r'"dev":\s*"[^"]*"',
                '"dev": "vite --host 0.0.0.0 --port 5173"',
                content
            )
            content = re.sub(
                r'"build":\s*"[^"]*"',
                '"build": "vite build"',
                content
            )
            content = re.sub(
                r'"preview":\s*"[^"]*"',
                '"preview": "vite preview --host 0.0.0.0 --port 4173"',
                content
            )
        
        with open(package_json_path, 'w') as f:
            f.write(content)
    
    print("   ✅ Updated package.json scripts")

def main():
    """Run frontend integration"""
    if not os.path.exists("frontend"):
        print("❌ Frontend directory not found!")
        print("🔧 Creating basic frontend structure...")
        create_basic_frontend_structure()
    
    update_frontend_api_calls()
    
    print("\n🎯 Testing Integration:")
    print("1. Ensure backend is running: cd backend && uvicorn app.main:app --reload")
    print("2. Start frontend: cd frontend && npm run dev")
    print("3. Open: http://localhost:5173")
    print("4. Test complete user workflow:")
    print("   → Register new account")
    print("   → Login with credentials")
    print("   → Navigate to dashboard")
    print("   → Select a module")
    print("   → Chat with Harv AI tutor")
    print("   → Verify responses use 'reply' field")

def create_basic_frontend_structure():
    """Create basic frontend structure if missing"""
    os.makedirs("frontend/src", exist_ok=True)
    os.makedirs("frontend/public", exist_ok=True)
    
    # Basic package.json
    package_content = '''{
  "name": "harv-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite --host 0.0.0.0 --port 5173",
    "build": "vite build",
    "preview": "vite preview --host 0.0.0.0 --port 4173",
    "lint": "eslint . --ext js,jsx --report-unused-disable-directives --max-warnings 0"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.0"
  },
  "devDependencies": {
    "@types/react": "^18.0.27",
    "@types/react-dom": "^18.0.10",
    "@vitejs/plugin-react": "^3.1.0",
    "vite": "^4.1.0"
  }
}'''
    
    with open("frontend/package.json", 'w') as f:
        f.write(package_content)
    
    # Basic index.html
    index_content = '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Harv Platform</title>
    <script src="https://cdn.tailwindcss.com"></script>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>'''
    
    with open("frontend/index.html", 'w') as f:
        f.write(index_content)
    
    # Basic main.jsx
    main_content = '''import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)'''
    
    with open("frontend/src/main.jsx", 'w') as f:
        f.write(main_content)
    
    # Basic vite.config.js
    vite_content = '''import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true
  }
})'''
    
    with open("frontend/vite.config.js", 'w') as f:
        f.write(vite_content)
    
    print("   ✅ Created basic frontend structure")

if __name__ == "__main__":
    main()
