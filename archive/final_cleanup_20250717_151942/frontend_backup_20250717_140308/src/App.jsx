import React, { useState, useEffect, useRef } from 'react';
import { User, MessageCircle, BookOpen, Download, LogOut, HelpCircle, CheckCircle, Send, Menu, X } from 'lucide-react';

// ==================== STYLES ====================
const styles = `
  @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600;700&display=swap');
  
  :root {
    --primary-green: #3E5641;
    --beige-bg: #D6CDB8;
    --standard-black: #222222;
    --accent-white: #FFFFFF;
    --light-green: #5a7a5e;
    --dark-green: #2d3f30;
    --warm-beige: #e0d7c2;
    --soft-shadow: rgba(62, 86, 65, 0.1);
  }

  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    font-family: 'Nunito', sans-serif;
    background-color: var(--beige-bg);
    color: var(--standard-black);
    line-height: 1.6;
  }

  .page {
    min-height: 100vh;
    background-color: var(--beige-bg);
  }

  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
  }

  .btn-primary {
    background-color: var(--primary-green);
    color: var(--accent-white);
    border: none;
    padding: 1rem 2rem;
    border-radius: 8px;
    font-family: 'Nunito', sans-serif;
    font-weight: 600;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.3s ease;
    min-height: 48px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
  }

  .btn-primary:hover {
    background-color: var(--dark-green);
    transform: translateY(-1px);
  }

  .btn-secondary {
    background-color: transparent;
    color: var(--primary-green);
    border: 2px solid var(--primary-green);
    padding: 1rem 2rem;
    border-radius: 8px;
    font-family: 'Nunito', sans-serif;
    font-weight: 600;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.3s ease;
    min-height: 48px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
  }

  .btn-secondary:hover {
    background-color: var(--primary-green);
    color: var(--accent-white);
  }

  .card {
    background-color: var(--accent-white);
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    border: 1px solid #e0e0e0;
    transition: all 0.3s ease;
    margin-bottom: 1rem;
  }

  .card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  }

  .form-group {
    margin-bottom: 1rem;
  }

  .form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 600;
    color: var(--primary-green);
  }

  .form-group input,
  .form-group select,
  .form-group textarea {
    width: 100%;
    padding: 0.75rem;
    border: 2px solid #e0e0e0;
    border-radius: 6px;
    font-family: 'Nunito', sans-serif;
    font-size: 1rem;
    transition: border-color 0.3s ease;
  }

  .form-group input:focus,
  .form-group select:focus,
  .form-group textarea:focus {
    outline: none;
    border-color: var(--primary-green);
  }

  .module-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    margin-top: 2rem;
  }

  .navbar {
    background-color: var(--primary-green);
    color: var(--accent-white);
    padding: 1rem 0;
    position: sticky;
    top: 0;
    z-index: 100;
  }

  .navbar-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .logo {
    font-family: 'Nunito', sans-serif;
    font-weight: 700;
    font-size: 1.5rem;
    color: var(--accent-white);
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  @media (max-width: 768px) {
    .module-grid {
      grid-template-columns: 1fr;
    }
  }
`;

// ==================== API SERVICE ====================
const API_BASE = 'http://127.0.0.1:8000';

const api = {
  // Auth endpoints
  register: async (email, password, onboardingData) => {
    try {
      const response = await fetch(`${API_BASE}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, ...onboardingData })
      });
      const data = await response.json();
      if (response.ok && data.access_token) {
        localStorage.setItem('access_token', data.access_token);
        return data;
      }
      throw new Error(data.detail || 'Registration failed');
    } catch (error) {
      throw error;
    }
  },

  login: async (email, password) => {
    try {
      const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const data = await response.json();
      if (response.ok && data.access_token) {
        localStorage.setItem('access_token', data.access_token);
        return data;
      }
      throw new Error(data.detail || 'Login failed');
    } catch (error) {
      throw error;
    }
  },

  // Module endpoints
  getModules: async () => {
    try {
      const response = await fetch(`${API_BASE}/modules`);
      return await response.json();
    } catch (error) {
      console.error('Failed to load modules:', error);
      return [];
    }
  },

  // Chat endpoints
  sendMessage: async (moduleId, message, conversationId = null) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE}/chat/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          module_id: moduleId,
          message: message,
          conversation_id: conversationId
        })
      });
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to send message:', error);
      throw error;
    }
  },

  // Health check
  healthCheck: async () => {
    try {
      const response = await fetch(`${API_BASE}/health`);
      return response.ok;
    } catch (error) {
      return false;
    }
  }
};

// ==================== COMPONENTS ====================

// Logo Component
const Logo = ({ size = 'medium', color = 'primary' }) => (
  <div className="logo" style={{
    fontSize: size === 'large' ? '3rem' : size === 'medium' ? '1.5rem' : '1.2rem',
    color: color === 'primary' ? 'var(--primary-green)' : 'var(--accent-white)'
  }}>
    <span>harv</span>
    <span style={{ fontSize: size === 'large' ? '2rem' : '1rem' }}>🌱</span>
  </div>
);

// Navbar Component
const Navbar = ({ user, onLogout, onNavigate }) => (
  <nav className="navbar">
    <div className="container">
      <div className="navbar-content">
        <Logo color="white" />
        {user && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <span>Welcome, {user.name || user.email}</span>
            <button 
              className="btn-secondary"
              onClick={onLogout}
              style={{ 
                color: 'var(--accent-white)',
                borderColor: 'var(--accent-white)',
                padding: '0.5rem 1rem',
                minHeight: 'auto'
              }}
            >
              <LogOut size={16} />
              Logout
            </button>
          </div>
        )}
      </div>
    </div>
  </nav>
);

// Landing Page
const LandingPage = ({ onNavigate }) => {
  const [backendStatus, setBackendStatus] = useState('checking');

  useEffect(() => {
    const checkBackend = async () => {
      const isHealthy = await api.healthCheck();
      setBackendStatus(isHealthy ? 'available' : 'unavailable');
    };
    checkBackend();
  }, []);

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: 'var(--beige-bg)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '2rem'
    }}>
      <div style={{ maxWidth: '600px', width: '100%', textAlign: 'center' }}>
        <Logo size="large" />
        
        <h1 style={{ 
          color: 'var(--primary-green)', 
          fontSize: '2.5rem',
          fontWeight: 700,
          marginBottom: '1rem',
          fontFamily: 'Nunito, sans-serif'
        }}>
          Welcome to Harv
        </h1>
        
        <p style={{ 
          color: 'var(--standard-black)', 
          fontSize: '1.2rem',
          marginBottom: '2rem',
          lineHeight: '1.6'
        }}>
          Your AI-powered Socratic learning companion for communication mastery
        </p>

        <div style={{ 
          marginBottom: '3rem',
          padding: '0.75rem 1.5rem',
          borderRadius: '8px',
          backgroundColor: backendStatus === 'available' ? '#d4edda' : '#f8d7da',
          color: backendStatus === 'available' ? '#155724' : '#721c24',
          fontSize: '1rem',
          fontWeight: 500
        }}>
          {backendStatus === 'checking' && '🔍 Connecting to Harv AI...'}
          {backendStatus === 'available' && '✅ Harv AI Ready'}
          {backendStatus === 'unavailable' && '⚠️ Harv AI Offline - Demo Mode'}
        </div>
        
        <div style={{ display: 'flex', gap: '1.5rem', justifyContent: 'center', flexWrap: 'wrap' }}>
          <button className="btn-primary" onClick={() => onNavigate('register')}>
            Register
          </button>
          <button className="btn-secondary" onClick={() => onNavigate('login')}>
            Login
          </button>
        </div>

        <div style={{ marginTop: '4rem', fontSize: '0.9rem', color: '#666' }}>
          <p>Powered by the Primer Initiative</p>
        </div>
      </div>
    </div>
  );
};

// Registration Page
const RegistrationPage = ({ onNavigate, onLogin }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    learningStyle: '',
    goals: '',
    experience: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const userData = await api.register(
        formData.email,
        formData.password,
        {
          name: formData.name,
          learning_style: formData.learningStyle,
          goals: formData.goals,
          experience: formData.experience
        }
      );
      onLogin(userData);
      onNavigate('dashboard');
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', padding: '2rem' }}>
        <div style={{ maxWidth: '500px', width: '100%' }}>
          <div className="card">
            <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
              <Logo />
              <h2 style={{ color: 'var(--primary-green)', marginBottom: '0.5rem' }}>Join Harv</h2>
              <p style={{ color: 'var(--standard-black)' }}>Create your account and start learning</p>
            </div>

            {error && (
              <div style={{ 
                padding: '1rem',
                backgroundColor: '#f8d7da',
                color: '#721c24',
                borderRadius: '6px',
                marginBottom: '1rem'
              }}>
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  required
                />
              </div>

              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  required
                />
              </div>

              <div className="form-group">
                <label>Password</label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  required
                />
              </div>

              <div className="form-group">
                <label>Learning Style</label>
                <select
                  value={formData.learningStyle}
                  onChange={(e) => setFormData({...formData, learningStyle: e.target.value})}
                  required
                >
                  <option value="">Select your learning style</option>
                  <option value="visual">Visual</option>
                  <option value="auditory">Auditory</option>
                  <option value="kinesthetic">Kinesthetic</option>
                  <option value="reading">Reading/Writing</option>
                </select>
              </div>

              <div className="form-group">
                <label>Learning Goals</label>
                <textarea
                  value={formData.goals}
                  onChange={(e) => setFormData({...formData, goals: e.target.value})}
                  placeholder="What do you hope to achieve with Harv?"
                  rows="3"
                />
              </div>

              <div className="form-group">
                <label>Communication Experience</label>
                <select
                  value={formData.experience}
                  onChange={(e) => setFormData({...formData, experience: e.target.value})}
                >
                  <option value="">Select your experience level</option>
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </div>

              <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem' }}>
                <button 
                  type="submit"
                  className="btn-primary" 
                  disabled={loading} 
                  style={{ flex: 1 }}
                >
                  {loading ? 'Creating Account...' : 'Create Account'}
                </button>
                <button 
                  type="button"
                  className="btn-secondary" 
                  onClick={() => onNavigate('landing')}
                >
                  Back
                </button>
              </div>
            </form>

            <div style={{ textAlign: 'center', marginTop: '1rem' }}>
              <span>Already have an account? </span>
              <button 
                style={{ background: 'none', border: 'none', color: 'var(--primary-green)', textDecoration: 'underline', cursor: 'pointer' }}
                onClick={() => onNavigate('login')}
              >
                Login here
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Login Page
const LoginPage = ({ onNavigate, onLogin }) => {
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const userData = await api.login(formData.email, formData.password);
      onLogin(userData);
      onNavigate('dashboard');
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', padding: '2rem' }}>
        <div style={{ maxWidth: '400px', width: '100%' }}>
          <div className="card">
            <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
              <Logo />
              <h2 style={{ color: 'var(--primary-green)', marginBottom: '0.5rem' }}>Welcome Back</h2>
              <p style={{ color: 'var(--standard-black)' }}>Login to continue your learning journey</p>
            </div>

            {error && (
              <div style={{ 
                padding: '1rem',
                backgroundColor: '#f8d7da',
                color: '#721c24',
                borderRadius: '6px',
                marginBottom: '1rem'
              }}>
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  required
                />
              </div>

              <div className="form-group">
                <label>Password</label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  required
                />
              </div>

              <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem' }}>
                <button 
                  type="submit"
                  className="btn-primary" 
                  disabled={loading} 
                  style={{ flex: 1 }}
                >
                  {loading ? 'Logging in...' : 'Login'}
                </button>
                <button 
                  type="button"
                  className="btn-secondary" 
                  onClick={() => onNavigate('landing')}
                >
                  Back
                </button>
              </div>
            </form>

            <div style={{ textAlign: 'center', marginTop: '1rem' }}>
              <span>Don't have an account? </span>
              <button 
                style={{ background: 'none', border: 'none', color: 'var(--primary-green)', textDecoration: 'underline', cursor: 'pointer' }}
                onClick={() => onNavigate('register')}
              >
                Register here
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Dashboard Page
const Dashboard = ({ user, onNavigate, onSelectModule, onLogout }) => {
  const [modules, setModules] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadModules = async () => {
      try {
        const moduleData = await api.getModules();
        setModules(Array.isArray(moduleData) ? moduleData : []);
      } catch (error) {
        console.error('Failed to load modules:', error);
        setModules([]);
      } finally {
        setLoading(false);
      }
    };
    loadModules();
  }, []);

  // Default modules if backend doesn't return any
  const defaultModules = [
    { id: 1, title: "Introduction to Communication Theory", description: "Foundational concepts and models of communication" },
    { id: 2, title: "Verbal Communication Skills", description: "Mastering spoken communication techniques" },
    { id: 3, title: "Non-Verbal Communication", description: "Understanding body language and visual cues" },
    { id: 4, title: "Active Listening", description: "Developing effective listening skills" },
    { id: 5, title: "Public Speaking", description: "Confidence and techniques for presentations" },
    { id: 6, title: "Interpersonal Communication", description: "Building relationships through communication" },
    { id: 7, title: "Group Communication", description: "Dynamics and strategies for group settings" },
    { id: 8, title: "Digital Communication", description: "Effective online and digital communication" },
    { id: 9, title: "Cross-Cultural Communication", description: "Navigating cultural differences in communication" },
    { id: 10, title: "Conflict Resolution", description: "Managing and resolving communication conflicts" },
    { id: 11, title: "Persuasive Communication", description: "Influencing and persuading through communication" },
    { id: 12, title: "Professional Communication", description: "Business and workplace communication skills" },
    { id: 13, title: "Media and Communication", description: "Understanding media's role in communication" },
    { id: 14, title: "Communication Ethics", description: "Ethical considerations in communication" },
    { id: 15, title: "Advanced Communication Strategies", description: "Sophisticated communication techniques" }
  ];

  const displayModules = modules.length > 0 ? modules : defaultModules;

  return (
    <div className="page">
      <Navbar user={user} onLogout={onLogout} onNavigate={onNavigate} />
      
      <div className="container" style={{ padding: '2rem 1rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
          <h1 style={{ color: 'var(--primary-green)', marginBottom: '1rem' }}>
            Welcome, {user?.name || user?.email || 'Student'}!
          </h1>
          <p style={{ fontSize: '1.1rem', color: 'var(--standard-black)' }}>
            Select a module to begin your Socratic learning journey
          </p>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '2rem' }}>
            <div style={{ fontSize: '1.2rem', color: 'var(--primary-green)' }}>Loading modules...</div>
          </div>
        ) : (
          <div className="module-grid">
            {displayModules.map((module) => (
              <div
                key={module.id}
                className="card"
                style={{ cursor: 'pointer' }}
                onClick={() => {
                  onSelectModule(module);
                  onNavigate('module');
                }}
              >
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
                  <div style={{ 
                    backgroundColor: 'var(--primary-green)', 
                    color: 'var(--accent-white)', 
                    padding: '0.5rem',
                    borderRadius: '6px',
                    minWidth: '40px',
                    textAlign: 'center',
                    fontWeight: 'bold'
                  }}>
                    {module.id}
                  </div>
                  <div style={{ flex: 1 }}>
                    <h3 style={{ color: 'var(--primary-green)', marginBottom: '0.5rem' }}>
                      {module.title}
                    </h3>
                    <p style={{ color: 'var(--standard-black)', fontSize: '0.9rem', lineHeight: '1.4' }}>
                      {module.description}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        <div style={{ textAlign: 'center', marginTop: '3rem' }}>
          <button className="btn-secondary" onClick={() => onNavigate('help')}>
            <HelpCircle size={16} />
            Need Help?
          </button>
        </div>
      </div>
    </div>
  );
};

// Module Page
const ModulePage = ({ module, user, onNavigate, onLogout }) => {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Add welcome message when module loads
    setMessages([
      {
        role: 'assistant',
        content: `Welcome to ${module.title}! I'm Harv, your Socratic learning companion. Instead of giving you direct answers, I'll guide you to discover knowledge through thoughtful questions. What would you like to explore about ${module.title.toLowerCase()}?`
      }
    ]);
  }, [module]);

  const handleSendMessage = async () => {
    if (!newMessage.trim()) return;

    const userMessage = { role: 'user', content: newMessage };
    setMessages(prev => [...prev, userMessage]);
    setNewMessage('');
    setLoading(true);

    try {
      const response = await api.sendMessage(module.id, newMessage, conversationId);
      
      if (response.conversation_id && !conversationId) {
        setConversationId(response.conversation_id);
      }

      const assistantMessage = {
        role: 'assistant',
        content: response.reply || response.message || "I'm here to help you discover the answer through questions. What do you think about this topic?"
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage = {
        role: 'assistant',
        content: "I'm having trouble connecting right now. Let me ask you this instead: What do you already know about this topic? How might you approach finding the answer?"
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const exportChat = (format) => {
    const content = messages.map(msg => 
      `${msg.role.toUpperCase()}: ${msg.content}`
    ).join('\n\n');
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${module.title.replace(/\s+/g, '_')}_conversation.${format}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="page">
      <Navbar user={user} onLogout={onLogout} onNavigate={onNavigate} />
      
      <div style={{ display: 'flex', height: 'calc(100vh - 80px)' }}>
        {/* Sidebar */}
        <div style={{
          width: '300px',
          backgroundColor: 'var(--accent-white)',
          padding: '1.5rem',
          borderRight: '1px solid #e0e0e0',
          overflowY: 'auto'
        }}>
          <button 
            className="btn-secondary" 
            onClick={() => onNavigate('dashboard')}
            style={{ width: '100%', marginBottom: '1rem' }}
          >
            ← Back to Dashboard
          </button>
          
          <h3 style={{ color: 'var(--primary-green)', marginBottom: '1rem' }}>
            {module.title}
          </h3>
          
          <div style={{ marginBottom: '2rem' }}>
            <h4 style={{ color: 'var(--standard-black)', marginBottom: '0.5rem' }}>Resources</h4>
            <ul style={{ listStyle: 'none', padding: 0 }}>
              <li style={{ padding: '0.5rem 0', borderBottom: '1px solid #e0e0e0' }}>
                <BookOpen size={16} style={{ marginRight: '0.5rem' }} />
                Lecture Materials
              </li>
              <li style={{ padding: '0.5rem 0', borderBottom: '1px solid #e0e0e0' }}>
                <BookOpen size={16} style={{ marginRight: '0.5rem' }} />
                Required Readings
              </li>
              <li style={{ padding: '0.5rem 0', borderBottom: '1px solid #e0e0e0' }}>
                <BookOpen size={16} style={{ marginRight: '0.5rem' }} />
                Supplemental Materials
              </li>
            </ul>
          </div>
          
          <div>
            <h4 style={{ color: 'var(--standard-black)', marginBottom: '0.5rem' }}>Export Chat</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <button 
                className="btn-secondary" 
                onClick={() => exportChat('txt')}
                style={{ fontSize: '0.9rem', padding: '0.5rem' }}
              >
                <Download size={14} />
                Export as TXT
              </button>
              <button 
                className="btn-secondary" 
                onClick={() => exportChat('txt')}
                style={{ fontSize: '0.9rem', padding: '0.5rem' }}
              >
                <Download size={14} />
                Export as PDF
              </button>
            </div>
          </div>
        </div>

        {/* Chat Area */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          {/* Chat Header */}
          <div style={{
            backgroundColor: 'var(--primary-green)',
            color: 'var(--accent-white)',
            padding: '1rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}>
            <MessageCircle size={24} />
            <h2 style={{ margin: 0 }}>Harv Chat</h2>
          </div>
          
          {/* Messages */}
          <div style={{
            flex: 1,
            padding: '1rem',
            overflowY: 'auto',
            backgroundColor: 'var(--accent-white)'
          }}>
            {messages.map((message, index) => (
              <div
                key={index}
                style={{
                  marginBottom: '1rem',
                  padding: '1rem',
                  borderRadius: '8px',
                  backgroundColor: message.role === 'user' ? 'var(--beige-bg)' : 'var(--primary-green)',
                  color: message.role === 'user' ? 'var(--standard-black)' : 'var(--accent-white)',
                  marginLeft: message.role === 'user' ? 'auto' : '0',
                  marginRight: message.role === 'user' ? '0' : 'auto',
                  maxWidth: '80%'
                }}
              >
                {message.content}
              </div>
            ))}
            
            {loading && (
              <div style={{
                padding: '1rem',
                fontStyle: 'italic',
                color: 'var(--primary-green)'
              }}>
                Harv is thinking...
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
          
          {/* Message Input */}
          <div style={{
            padding: '1rem',
            backgroundColor: 'var(--accent-white)',
            borderTop: '1px solid #e0e0e0',
            display: 'flex',
            gap: '0.5rem'
          }}>
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask Harv a question..."
              style={{
                flex: 1,
                padding: '0.75rem',
                border: '1px solid #e0e0e0',
                borderRadius: '6px',
                fontFamily: 'Nunito, sans-serif'
              }}
              disabled={loading}
            />
            <button
              onClick={handleSendMessage}
              disabled={loading || !newMessage.trim()}
              style={{
                backgroundColor: 'var(--primary-green)',
                color: 'var(--accent-white)',
                border: 'none',
                padding: '0.75rem 1.5rem',
                borderRadius: '6px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                fontFamily: 'Nunito, sans-serif'
              }}
            >
              <Send size={16} />
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Help Page
const HelpPage = ({ user, onNavigate, onLogout }) => {
  const [openSection, setOpenSection] = useState('getting-started');

  const faqData = [
    {
      id: 'getting-started',
      title: 'Getting Started',
      content: 'Harv uses the Socratic method to help you learn. Instead of giving direct answers, Harv will ask you questions to guide your thinking and help you discover knowledge yourself.'
    },
    {
      id: 'modules',
      title: 'How do modules work?',
      content: 'Each module focuses on a specific aspect of communication. You can work through them in any order, and each conversation builds on your previous learning.'
    },
    {
      id: 'conversations',
      title: 'Managing conversations',
      content: 'You can have multiple conversations per module. Each conversation is saved, and you can export them as TXT or PDF files for your records.'
    },
    {
      id: 'learning-style',
      title: 'Personalized learning',
      content: 'Harv adapts to your learning style based on your onboarding survey and interaction patterns. The AI remembers your progress and adjusts accordingly.'
    },
    {
      id: 'technical',
      title: 'Technical support',
      content: 'If you encounter technical issues, try refreshing the page first. If problems persist, contact your instructor or system administrator.'
    }
  ];

  return (
    <div className="page">
      <Navbar user={user} onLogout={onLogout} onNavigate={onNavigate} />
      
      <div className="container" style={{ padding: '2rem 1rem', maxWidth: '800px' }}>
        <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
          <h1 style={{ color: 'var(--primary-green)', marginBottom: '1rem' }}>
            Help & FAQ
          </h1>
          <p style={{ fontSize: '1.1rem', color: 'var(--standard-black)' }}>
            Find answers to common questions about using Harv
          </p>
        </div>

        <div style={{ marginBottom: '2rem' }}>
          <button 
            className="btn-secondary" 
            onClick={() => onNavigate('dashboard')}
          >
            ← Back to Dashboard
          </button>
        </div>

        <div>
          {faqData.map((faq) => (
            <div key={faq.id} className="card" style={{ marginBottom: '1rem' }}>
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  cursor: 'pointer'
                }}
                onClick={() => setOpenSection(openSection === faq.id ? '' : faq.id)}
              >
                <h3 style={{ color: 'var(--primary-green)', margin: 0 }}>
                  {faq.title}
                </h3>
                <span style={{ fontSize: '1.5rem', color: 'var(--primary-green)' }}>
                  {openSection === faq.id ? '−' : '+'}
                </span>
              </div>
              
              {openSection === faq.id && (
                <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid #e0e0e0' }}>
                  <p style={{ color: 'var(--standard-black)', lineHeight: '1.6' }}>
                    {faq.content}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// ==================== MAIN APP ====================
const App = () => {
  const [currentPage, setCurrentPage] = useState('landing');
  const [user, setUser] = useState(null);
  const [selectedModule, setSelectedModule] = useState(null);

  // Check for existing auth token on load
  useEffect(() => {
    // Clear any existing tokens to start fresh
    localStorage.removeItem('access_token');
    setCurrentPage('landing');
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
    setCurrentPage('dashboard');
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    setUser(null);
    setCurrentPage('landing');
  };

  const handleSelectModule = (module) => {
    setSelectedModule(module);
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'landing':
        return <LandingPage onNavigate={setCurrentPage} />;
      
      case 'register':
        return <RegistrationPage onNavigate={setCurrentPage} onLogin={handleLogin} />;
      
      case 'login':
        return <LoginPage onNavigate={setCurrentPage} onLogin={handleLogin} />;
      
      case 'dashboard':
        return (
          <Dashboard 
            user={user} 
            onNavigate={setCurrentPage} 
            onSelectModule={handleSelectModule}
            onLogout={handleLogout}
          />
        );
      
      case 'module':
        return (
          <ModulePage 
            module={selectedModule} 
            user={user}
            onNavigate={setCurrentPage}
            onLogout={handleLogout}
          />
        );
      
      case 'help':
        return (
          <HelpPage 
            user={user}
            onNavigate={setCurrentPage}
            onLogout={handleLogout}
          />
        );
      
      default:
        return <LandingPage onNavigate={setCurrentPage} />;
    }
  };

  return (
    <div>
      <style dangerouslySetInnerHTML={{ __html: styles }} />
      {renderPage()}
    </div>
  );
};

export default App;
