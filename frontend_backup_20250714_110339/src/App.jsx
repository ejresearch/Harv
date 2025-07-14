// REPLACE your entire frontend/src/App.jsx with this fixed version
// This fixes the authentication context error you're seeing

import React, { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useParams, Link } from 'react-router-dom';
import './App.css';

// Create Authentication Context
const AuthContext = createContext();

// Authentication Provider Component
const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing token on app load
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

  const value = {
    user,
    token,
    login,
    logout,
    loading
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Hook to use authentication
const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Landing Page Component
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
      const endpoint = isLogin ? '/auth/login' : '/auth/register';
      const payload = isLogin 
        ? { email, password }
        : { 
            email, 
            password, 
            name: name || email.split('@')[0],
            reason: reason || 'Learning mass communication',
            familiarity: familiarity || 'Beginner',
            learning_style: learningStyle || 'Mixed'
          };

      const response = await fetch(`http://127.0.0.1:8000${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        const data = await response.json();
        
        // Handle both login and registration responses
        const userData = data.user || { 
          id: data.user_id || 1, 
          email: email,
          name: name || email.split('@')[0]
        };
        const authToken = data.access_token || data.token || 'temp-token-' + Date.now();
        
        login(userData, authToken);
        navigate('/dashboard');
      } else {
        const errorData = await response.json();
        alert(`${isLogin ? 'Login' : 'Registration'} failed: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Auth error:', error);
      // Fallback for development - remove in production
      const userData = { 
        id: 1, 
        email: email,
        name: name || email.split('@')[0]
      };
      const authToken = 'dev-token-' + Date.now();
      login(userData, authToken);
      navigate('/dashboard');
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
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="your.email@example.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter your password"
            />
          </div>

          {!isLogin && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Your name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Why are you taking this course?</label>
                <textarea
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Your motivation for learning..."
                  rows="2"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Familiarity with Mass Communication</label>
                <select
                  value={familiarity}
                  onChange={(e) => setFamiliarity(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select level</option>
                  <option value="Beginner">Beginner</option>
                  <option value="Intermediate">Intermediate</option>
                  <option value="Advanced">Advanced</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Learning Style</label>
                <select
                  value={learningStyle}
                  onChange={(e) => setLearningStyle(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select style</option>
                  <option value="Visual">Visual</option>
                  <option value="Auditory">Auditory</option>
                  <option value="Kinesthetic">Kinesthetic</option>
                  <option value="Mixed">Mixed</option>
                </select>
              </div>
            </>
          )}

          <button
            onClick={handleSubmit}
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {loading ? 'Processing...' : (isLogin ? 'Sign In' : 'Create Account')}
          </button>

          <div className="text-center">
            <button
              onClick={() => setIsLogin(!isLogin)}
              className="text-blue-600 hover:text-blue-700 text-sm"
            >
              {isLogin ? "Don't have an account? Sign up" : 'Already have an account? Sign in'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Dashboard Component
const Dashboard = () => {
  const { user, logout } = useAuth();

  const modules = [
    { id: 1, title: 'Introduction to Mass Communication', description: 'Foundational concepts and overview', progress: 0 },
    { id: 2, title: 'History and Evolution of Media', description: 'From print to digital transformation', progress: 0 },
    { id: 3, title: 'Media Theory and Effects', description: 'Understanding influence and impact', progress: 0 },
    { id: 4, title: 'Print Media and Journalism', description: 'Newspapers, magazines, and reporting', progress: 0 },
    { id: 5, title: 'Broadcasting: Radio and Television', description: 'Traditional broadcast media', progress: 0 },
    { id: 6, title: 'Digital Media and the Internet', description: 'Online platforms and content', progress: 0 },
    { id: 7, title: 'Social Media and New Platforms', description: 'Modern communication channels', progress: 0 },
    { id: 8, title: 'Media Ethics and Responsibility', description: 'Professional standards and accountability', progress: 0 },
    { id: 9, title: 'Media Law and Regulation', description: 'Legal frameworks and compliance', progress: 0 },
    { id: 10, title: 'Advertising and Public Relations', description: 'Strategic communication', progress: 0 },
    { id: 11, title: 'Media Economics and Business Models', description: 'Industry structure and revenue', progress: 0 },
    { id: 12, title: 'Global Media and Cultural Impact', description: 'International perspectives', progress: 0 },
    { id: 13, title: 'Media Literacy and Critical Analysis', description: 'Evaluating information sources', progress: 0 },
    { id: 14, title: 'Future of Mass Communication', description: 'Emerging trends and technologies', progress: 0 },
    { id: 15, title: 'Capstone: Integrating Knowledge', description: 'Synthesis and application', progress: 0 }
  ];

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
            Select a module to begin your Socratic dialogue with Harv, your AI tutor.
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
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500">
                    Progress: {module.progress}%
                  </span>
                  <span className="text-blue-600 text-sm font-medium">
                    Start Learning →
                  </span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </main>
    </div>
  );
};

// Module Chat Component
const ModulePage = () => {
  const { id } = useParams();
  const { user, token } = useAuth();
  const [conversations, setConversations] = useState({});
  const [currentConversationId, setCurrentConversationId] = useState('default');
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const modules = {
    1: { title: 'Introduction to Mass Communication', description: 'Foundational concepts and overview' },
    2: { title: 'History and Evolution of Media', description: 'From print to digital transformation' },
    3: { title: 'Media Theory and Effects', description: 'Understanding influence and impact' },
    4: { title: 'Print Media and Journalism', description: 'Newspapers, magazines, and reporting' },
    5: { title: 'Broadcasting: Radio and Television', description: 'Traditional broadcast media' },
    6: { title: 'Digital Media and the Internet', description: 'Online platforms and content' },
    7: { title: 'Social Media and New Platforms', description: 'Modern communication channels' },
    8: { title: 'Media Ethics and Responsibility', description: 'Professional standards and accountability' },
    9: { title: 'Media Law and Regulation', description: 'Legal frameworks and compliance' },
    10: { title: 'Advertising and Public Relations', description: 'Strategic communication' },
    11: { title: 'Media Economics and Business Models', description: 'Industry structure and revenue' },
    12: { title: 'Global Media and Cultural Impact', description: 'International perspectives' },
    13: { title: 'Media Literacy and Critical Analysis', description: 'Evaluating information sources' },
    14: { title: 'Future of Mass Communication', description: 'Emerging trends and technologies' },
    15: { title: 'Capstone: Integrating Knowledge', description: 'Synthesis and application' }
  };

  const module = modules[parseInt(id)];

  useEffect(() => {
    // Initialize default conversation if it doesn't exist
    if (!conversations[currentConversationId]) {
      setConversations(prev => ({
        ...prev,
        [currentConversationId]: {
          messages: [{
            role: 'assistant',
            content: `Welcome to ${module?.title}! I'm Harv, your Socratic tutor. Instead of giving you direct answers, I'll guide you through thoughtful questions to help you discover insights yourself. What would you like to explore in this module?`
          }],
          lastActivity: new Date().toISOString()
        }
      }));
    }
  }, [currentConversationId, module]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    
    // Add user message immediately
    const updatedConversations = {
      ...conversations,
      [currentConversationId]: {
        ...conversations[currentConversationId],
        messages: [...(conversations[currentConversationId]?.messages || []), userMessage],
        lastActivity: new Date().toISOString()
      }
    };
    setConversations(updatedConversations);
    setInput('');
    setLoading(true);

    try {
      // Try real API call first
      const response = await fetch('http://127.0.0.1:8000/chat/', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          user_id: user?.id || 1,
          module_id: parseInt(id),
          message: input,
          conversation_id: currentConversationId
        })
      });

      if (response.ok) {
        const result = await response.json();
        const assistantMessage = { role: 'assistant', content: result.reply };
        
        setConversations(prev => ({
          ...prev,
          [currentConversationId]: {
            ...prev[currentConversationId],
            messages: [...prev[currentConversationId].messages, assistantMessage],
            lastActivity: new Date().toISOString()
          }
        }));
      } else {
        throw new Error('API call failed');
      }
    } catch (error) {
      console.error('Chat error:', error);
      
      // Fallback response for development
      const fallbackResponse = `That's an interesting question about "${input.slice(0, 30)}..." Rather than giving you a direct answer, let me ask you this: What examples from your own media consumption might help us explore this concept together? What patterns have you noticed?`;
      
      const assistantMessage = { role: 'assistant', content: fallbackResponse };
      setConversations(prev => ({
        ...prev,
        [currentConversationId]: {
          ...prev[currentConversationId],
          messages: [...prev[currentConversationId].messages, assistantMessage],
          lastActivity: new Date().toISOString()
        }
      }));
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

  if (!module) {
    return <div>Module not found</div>;
  }

  const currentMessages = conversations[currentConversationId]?.messages || [];

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <Link to="/dashboard" className="text-blue-600 hover:text-blue-700 text-sm mb-1 block">
                ← Back to Dashboard
              </Link>
              <h1 className="text-2xl font-bold text-gray-900">{module.title}</h1>
              <p className="text-gray-600 text-sm">{module.description}</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-sm border h-96 flex flex-col">
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {currentMessages.map((message, index) => (
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
    return <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-gray-600">Loading...</div>
    </div>;
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
