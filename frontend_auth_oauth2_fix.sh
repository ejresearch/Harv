#!/bin/bash
# Frontend OAuth2 Authentication Fix
# Run from root directory: bash frontend_auth_oauth2_fix.sh

echo "Fixing Frontend Authentication for OAuth2 Format"
echo "================================================"

# 1. First, fix the API service
echo "1. Updating API service..."
cat > frontend/src/services/api.js << 'EOF'
// Updated API Service with OAuth2 Authentication
const BASE_URL = 'http://127.0.0.1:8000';

class ApiService {
  constructor() {
    this.token = localStorage.getItem('token');
  }

  // Login using OAuth2 format (working format!)
  async login(credentials) {
    const formData = new URLSearchParams();
    formData.append('username', credentials.email);  // Backend expects 'username'
    formData.append('password', credentials.password);
    formData.append('grant_type', 'password');

    const response = await fetch(`${BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData
    });

    const data = await response.json();
    
    if (response.ok) {
      this.token = data.access_token;
      localStorage.setItem('token', this.token);
      return {
        success: true,
        access_token: data.access_token,
        user: data.user
      };
    } else {
      throw new Error(data.detail || 'Login failed');
    }
  }

  // Register (JSON format works for registration)
  async register(userData) {
    const response = await fetch(`${BASE_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData)
    });

    const data = await response.json();
    
    if (response.ok) {
      return {
        success: true,
        user: data.user || data,
        message: data.message || 'Registration successful'
      };
    } else {
      throw new Error(data.detail || 'Registration failed');
    }
  }

  // Authenticated API calls
  async apiCall(endpoint, method = 'GET', data = null) {
    const headers = {
      'Authorization': `Bearer ${this.token}`,
    };

    const options = { method, headers };

    if (data && method !== 'GET') {
      if (endpoint.includes('/chat')) {
        headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(data);
      } else {
        headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(data);
      }
    }

    const response = await fetch(`${BASE_URL}${endpoint}`, options);
    
    if (!response.ok) {
      throw new Error(`API call failed: ${response.status}`);
    }
    
    return await response.json();
  }

  // Get modules
  async getModules() {
    return this.apiCall('/modules');
  }

  // Send chat message
  async sendMessage(message, moduleId = 1) {
    return this.apiCall('/chat/', 'POST', {
      message: message,
      module_id: moduleId
    });
  }

  // Get memory stats
  async getMemoryStats(userId) {
    return this.apiCall(`/memory/stats/${userId}`);
  }

  // Logout
  logout() {
    this.token = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }
}

export default new ApiService();
EOF

echo "   ✅ Updated API service with OAuth2 authentication"

# 2. Update App.jsx to use the fixed API service
echo "2. Updating App.jsx authentication handling..."
cat > frontend/src/App.jsx << 'EOF'
import React, { useState, useEffect, createContext, useContext } from 'react';
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
        ApiService.token = storedToken;
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
    ApiService.token = authToken;
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    ApiService.logout();
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

// Landing Page with Fixed Authentication
const LandingPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [name, setName] = useState('');
  const [error, setError] = useState('');

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!email || !password) {
      setError('Please fill in all required fields');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      if (isLogin) {
        // Login using OAuth2 format
        console.log('Attempting login with OAuth2 format...');
        const response = await ApiService.login({ email, password });
        
        if (response.success) {
          login(response.user, response.access_token);
          navigate('/dashboard');
        }
      } else {
        // Register using JSON format
        console.log('Attempting registration...');
        const response = await ApiService.register({
          email,
          password,
          name: name || email.split('@')[0],
          reason: 'Learning mass communication',
          familiarity: 'Beginner',
          learning_style: 'Mixed'
        });
        
        if (response.success) {
          setError('');
          alert('Registration successful! Please login.');
          setIsLogin(true);
        }
      }
    } catch (error) {
      console.error('Auth error:', error);
      setError(error.message || `${isLogin ? 'Login' : 'Registration'} failed`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Harv Platform
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            AI-Powered Socratic Learning System
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                placeholder="Email address"
              />
            </div>
            <div>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                placeholder="Password"
              />
            </div>
            {!isLogin && (
              <div>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                  placeholder="Full Name (optional)"
                />
              </div>
            )}
          </div>

          {error && (
            <div className="text-red-600 text-sm text-center">{error}</div>
          )}

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {loading ? 'Processing...' : (isLogin ? 'Sign In' : 'Sign Up')}
            </button>
          </div>

          <div className="text-center">
            <button
              type="button"
              onClick={() => {
                setIsLogin(!isLogin);
                setError('');
              }}
              className="text-blue-600 hover:text-blue-500"
            >
              {isLogin ? "Don't have an account? Sign up" : "Already have an account? Sign in"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Dashboard Component
const Dashboard = () => {
  const { user, logout } = useAuth();
  const [modules, setModules] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const loadModules = async () => {
      try {
        const response = await ApiService.getModules();
        setModules(response.modules || response || []);
      } catch (error) {
        console.error('Error loading modules:', error);
      } finally {
        setLoading(false);
      }
    };
    
    loadModules();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold">Harv Platform</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">Welcome, {user?.name || user?.email}</span>
              <button
                onClick={logout}
                className="text-gray-500 hover:text-gray-700"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Communication Modules</h2>
          
          {loading ? (
            <div className="text-center">Loading modules...</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {modules.map((module) => (
                <Link
                  key={module.id}
                  to={`/module/${module.id}`}
                  className="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow"
                >
                  <div className="p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      {module.name || module.title}
                    </h3>
                    <p className="text-gray-600 text-sm">
                      {module.description}
                    </p>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

// Module Page Component
const ModulePage = () => {
  const { id } = useParams();
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await ApiService.sendMessage(input, parseInt(id));
      const aiMessage = { 
        role: 'assistant', 
        content: response.reply || response.response || 'I received your message.'
      };
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      };
      setMessages(prev => [...prev, errorMessage]);
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
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link to="/dashboard" className="text-blue-600 hover:text-blue-500 mr-4">
                ← Back to Dashboard
              </Link>
              <h1 className="text-xl font-semibold">Module {id}</h1>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-4xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="bg-white shadow rounded-lg h-96 flex flex-col">
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

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">Loading...</div>
      </div>
    );
  }
  
  return user ? children : <Navigate to="/" replace />;
};

// Main App Component
function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
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
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
EOF

echo "   ✅ Updated App.jsx with proper OAuth2 authentication"

# 3. Test the frontend
echo "3. Creating frontend test script..."
cat > test_frontend_auth.py << 'EOF'
#!/usr/bin/env python3
"""
Test Frontend Authentication Fix
"""
import subprocess
import time
import requests
import webbrowser

def start_frontend():
    """Start the React frontend"""
    print("Starting React frontend...")
    try:
        # Check if frontend is already running
        response = requests.get("http://localhost:5173", timeout=2)
        print("   ✅ Frontend already running on http://localhost:5173")
        return True
    except:
        pass
    
    try:
        # Start frontend
        subprocess.Popen(
            ['npm', 'run', 'dev'],
            cwd='frontend',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for startup
        print("   ⏳ Waiting for frontend to start...")
        for i in range(30):
            try:
                response = requests.get("http://localhost:5173", timeout=1)
                print("   ✅ Frontend started successfully!")
                return True
            except:
                time.sleep(1)
                
        print("   ❌ Frontend failed to start")
        return False
        
    except Exception as e:
        print(f"   ❌ Error starting frontend: {e}")
        return False

def test_auth_flow():
    """Test the authentication flow"""
    print("\n🧪 Testing Authentication Flow")
    print("==============================")
    
    # Test backend is running
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Backend is running")
        else:
            print("   ❌ Backend health check failed")
            return False
    except:
        print("   ❌ Backend is not running")
        print("   💡 Start backend: cd backend && uvicorn app.main:app --reload")
        return False
    
    # Test OAuth2 login format
    try:
        login_data = {
            "username": "questfortheprimer@gmail.com",
            "password": "Joust?poet1c",
            "grant_type": "password"
        }
        
        response = requests.post(
            "http://127.0.0.1:8000/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            print("   ✅ OAuth2 login format working")
            return True
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Login test error: {e}")
        return False

def main():
    print("🔧 Frontend Authentication Fix Test")
    print("===================================")
    
    backend_ok = test_auth_flow()
    
    if backend_ok:
        frontend_ok = start_frontend()
        
        if frontend_ok:
            print("\n🎉 SUCCESS!")
            print("===========")
            print("✅ Backend: Running with OAuth2 authentication")
            print("✅ Frontend: Running with fixed authentication")
            print("")
            print("🌐 Access your platform:")
            print("   Frontend: http://localhost:5173")
            print("   Backend:  http://localhost:8000")
            print("")
            print("🧪 Test Authentication:")
            print("   1. Go to http://localhost:5173")
            print("   2. Try creating an account")
            print("   3. Try logging in")
            print("   4. Should work without 422 errors!")
            
            # Open browser
            try:
                webbrowser.open("http://localhost:5173")
            except:
                pass
                
        else:
            print("\n⚠️  Frontend startup failed")
            print("Manual steps:")
            print("1. cd frontend")
            print("2. npm install")
            print("3. npm run dev")
    else:
        print("\n⚠️  Backend authentication needs to be fixed first")
        print("Make sure backend is running: cd backend && uvicorn app.main:app --reload")

if __name__ == "__main__":
    main()
EOF

echo "   ✅ Created frontend test script"

echo ""
echo "✅ Frontend OAuth2 Authentication Fix Complete!"
echo "==============================================="
echo ""
echo "🔧 What was fixed:"
echo "   ✅ API service now uses OAuth2 format (username + form data)"
echo "   ✅ Login sends form data instead of JSON"
echo "   ✅ Registration still uses JSON (which works)"
echo "   ✅ Proper error handling and user feedback"
echo ""
echo "🚀 Next steps:"
echo "   1. Run the test: python test_frontend_auth.py"
echo "   2. Frontend will start on http://localhost:5173"
echo "   3. Try creating an account - should work now!"
echo ""
echo "💡 The key fix:"
echo "   - Login now uses OAuth2 format with 'username' field"
echo "   - This matches your backend's expected authentication format"
echo "   - No more 422 errors on login!"
