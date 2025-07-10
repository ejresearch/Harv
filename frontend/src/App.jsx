import React, { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Send, Download, FileText, Loader2, Sun, Moon, Plus, MessageSquare, BookOpen, Monitor, LogOut, User, HelpCircle, Mail, MessageCircle, ChevronDown, Upload, X } from 'lucide-react';

// Auth Context
const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));

  const login = (userData, userToken) => {
    setUser(userData);
    setToken(userToken);
    localStorage.setItem('token', userToken);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  };

  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser && token) {
      setUser(JSON.parse(savedUser));
    }
  }, [token]);

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => useContext(AuthContext);

// Drag and Drop Component
const DragDropUpload = ({ onFilesUploaded, accept = "*", multiple = true, className = "" }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  };

  const handleFileInput = (e) => {
    const files = Array.from(e.target.files);
    handleFiles(files);
  };

  const handleFiles = (files) => {
    const newFiles = files.map(file => ({
      id: Date.now() + Math.random(),
      file,
      name: file.name,
      size: file.size,
      type: file.type,
      status: 'uploaded'
    }));
    
    setUploadedFiles(prev => [...prev, ...newFiles]);
    onFilesUploaded && onFilesUploaded(newFiles);
  };

  const removeFile = (fileId) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className={className}>
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
          isDragging 
            ? 'border-[#3E5641] bg-[#3E5641] bg-opacity-10' 
            : 'border-gray-300 hover:border-[#3E5641]'
        }`}
      >
        <Upload size={32} className={`mx-auto mb-4 ${isDragging ? 'text-[#3E5641]' : 'text-gray-400'}`} />
        <p className="text-lg font-medium text-gray-700 mb-2">
          {isDragging ? 'Drop files here' : 'Drag and drop files here'}
        </p>
        <p className="text-sm text-gray-500 mb-4">or click to browse</p>
        <input
          type="file"
          multiple={multiple}
          accept={accept}
          onChange={handleFileInput}
          className="hidden"
          id="file-upload"
        />
        <label
          htmlFor="file-upload"
          className="inline-block px-6 py-2 bg-[#3E5641] text-white rounded-lg cursor-pointer hover:bg-[#2D3F2F] transition-colors"
        >
          Choose Files
        </label>
      </div>

      {uploadedFiles.length > 0 && (
        <div className="mt-6">
          <h4 className="font-semibold text-gray-800 mb-3">Uploaded Files</h4>
          <div className="space-y-2">
            {uploadedFiles.map((file) => (
              <div key={file.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <FileText size={16} className="text-[#3E5641]" />
                  <div>
                    <p className="font-medium text-gray-800">{file.name}</p>
                    <p className="text-sm text-gray-500">{formatFileSize(file.size)}</p>
                  </div>
                </div>
                <button
                  onClick={() => removeFile(file.id)}
                  className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                >
                  <X size={16} />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { token } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!token) {
      navigate('/');
    }
  }, [token, navigate]);

  return token ? children : null;
};

// Landing Page Component
const LandingPage = () => {
  const [darkMode, setDarkMode] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      setDarkMode(savedTheme === 'dark');
    } else {
      setDarkMode(window.matchMedia('(prefers-color-scheme: dark)').matches);
    }
  }, []);

  const toggleTheme = () => {
    const newDarkMode = !darkMode;
    setDarkMode(newDarkMode);
    localStorage.setItem('theme', newDarkMode ? 'dark' : 'light');
  };

  const handleRegister = () => {
    navigate('/register');
  };

  const handleLogin = () => {
    navigate('/login');
  };

  const themeClasses = {
    bg: darkMode ? 'bg-gray-900' : 'bg-[#D6CDB8]',
    text: darkMode ? 'text-white' : 'text-[#222222]',
    textMuted: darkMode ? 'text-gray-400' : 'text-[#222222]',
    button: darkMode ? 'bg-white text-gray-900 hover:bg-gray-100' : 'bg-[#3E5641] text-white hover:bg-[#2D3F2F]',
    buttonSecondary: darkMode ? 'border-gray-600 text-gray-300 hover:bg-gray-800' : 'border-[#3E5641] text-[#3E5641] hover:bg-[#3E5641] hover:text-white'
  };

  return (
    <div className={`min-h-screen ${themeClasses.bg} flex items-center justify-center px-6`} style={{ fontFamily: 'Nunito, sans-serif' }}>
      <button
        onClick={toggleTheme}
        className={`fixed top-6 right-6 p-3 rounded-lg ${darkMode ? 'text-gray-400 hover:text-gray-200' : 'text-[#3E5641] hover:text-[#222222]'} transition-colors`}
      >
        {darkMode ? <Sun size={24} /> : <Moon size={24} />}
      </button>

      <div className="w-full max-w-lg text-center">
        <div className="mb-16">
          <div className="mb-6">
            <div className={`text-6xl font-bold ${themeClasses.text} mb-2 tracking-tight`} style={{ fontFamily: 'Nunito, sans-serif' }}>
              <span className="relative">
                h
                <span className="absolute -top-2 -right-1 text-[#3E5641] text-2xl">🌿</span>
                arv
              </span>
            </div>
          </div>
          <h1 className={`text-3xl font-semibold ${themeClasses.text} tracking-tight mb-3`}>
            Primer Initiative
          </h1>
          <p className={`${themeClasses.textMuted} text-lg leading-relaxed`}>
            AI-powered Socratic learning for mass communication
          </p>
        </div>

        <div className="space-y-4 mb-12">
          <button
            onClick={handleRegister}
            className={`w-full py-4 px-8 rounded-lg text-lg font-semibold transition-colors ${themeClasses.button} shadow-sm`}
          >
            Register
          </button>
          <button
            onClick={handleLogin}
            className={`w-full py-4 px-8 border-2 rounded-lg text-lg font-semibold transition-colors ${themeClasses.buttonSecondary}`}
          >
            Login
          </button>
        </div>

        <div className={`text-base ${themeClasses.textMuted} leading-relaxed max-w-md mx-auto`}>
          <p className="mb-4">
            Engage with 15 interactive modules designed to guide your learning through thoughtful dialogue with AI tutors.
          </p>
          <p>
            Discover insights through questions, not answers.
          </p>
        </div>

        <div className="mt-16 flex items-center justify-center gap-3">
          <div className="w-2 h-2 bg-[#3E5641] rounded-full"></div>
          <span className={`text-sm ${themeClasses.textMuted} font-medium`}>
            Socratic Method • Personalized Learning • Expert Guidance
          </span>
          <div className="w-2 h-2 bg-[#3E5641] rounded-full"></div>
        </div>
      </div>
    </div>
  );
};

// Login Page Component
const LoginPage = () => {
  const [darkMode, setDarkMode] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = () => {
    if (email && password) {
      setLoading(true);
      setTimeout(() => {
        setLoading(false);
        // Mock login
        const userData = { name: email.split('@')[0], email };
        const token = 'mock-jwt-token';
        login(userData, token);
        navigate('/dashboard');
      }, 1000);
    } else {
      alert('Please fill in all fields');
    }
  };

  const themeClasses = {
    bg: darkMode ? 'bg-gray-900' : 'bg-[#D6CDB8]',
    cardBg: darkMode ? 'bg-gray-800' : 'bg-white',
    text: darkMode ? 'text-white' : 'text-[#222222]',
    textMuted: darkMode ? 'text-gray-400' : 'text-[#222222]',
    input: darkMode 
      ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400 focus:ring-[#3E5641] focus:border-[#3E5641]' 
      : 'bg-white border-gray-300 text-[#222222] placeholder-gray-500 focus:ring-[#3E5641] focus:border-[#3E5641]',
    button: darkMode 
      ? 'bg-white text-gray-900 hover:bg-gray-100' 
      : 'bg-[#3E5641] text-white hover:bg-[#2D3F2F]'
  };

  return (
    <div className={`min-h-screen ${themeClasses.bg} flex items-center justify-center px-6`} style={{ fontFamily: 'Nunito, sans-serif' }}>
      <div className="w-full max-w-md">
        <button
          onClick={() => navigate('/')}
          className="text-gray-600 hover:text-gray-800 mb-8 flex items-center gap-2 text-base transition-colors"
        >
          <ArrowLeft size={20} />
          Back
        </button>
        
        <div className={`${themeClasses.cardBg} rounded-xl p-8 shadow-lg`}>
          <div className="text-center mb-8">
            <div className={`text-3xl font-bold ${themeClasses.text} mb-2`}>
              <span className="relative">
                h<span className="absolute -top-1 -right-1 text-[#3E5641] text-lg">🌿</span>arv
              </span>
            </div>
            <h1 className={`text-2xl font-semibold ${themeClasses.text} mb-2`}>Welcome Back</h1>
            <p className={`text-base ${themeClasses.textMuted}`}>Sign in to continue learning</p>
          </div>

          <div className="space-y-4">
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email Address"
              className={`w-full px-4 py-4 border rounded-lg text-base focus:outline-none focus:ring-2 ${themeClasses.input}`}
            />
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              className={`w-full px-4 py-4 border rounded-lg text-base focus:outline-none focus:ring-2 ${themeClasses.input}`}
            />
            <button
              onClick={handleSubmit}
              disabled={loading}
              className={`w-full py-4 rounded-lg text-lg font-semibold transition-colors disabled:opacity-50 flex items-center justify-center ${themeClasses.button}`}
            >
              {loading ? <Loader2 className="animate-spin mr-2" size={20} /> : null}
              {loading ? 'Signing In...' : 'Sign In'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Register Page Component
const RegisterPage = () => {
  const [darkMode, setDarkMode] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [reason, setReason] = useState('');
  const [familiarity, setFamiliarity] = useState('');
  const [learningStyle, setLearningStyle] = useState('');
  const [goals, setGoals] = useState('');
  const [background, setBackground] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = () => {
    if (email && password && name && reason && familiarity && learningStyle) {
      setLoading(true);
      setTimeout(() => {
        setLoading(false);
        // Mock registration and login
        const userData = { name, email };
        const token = 'mock-jwt-token';
        login(userData, token);
        navigate('/dashboard');
      }, 2000);
    } else {
      alert('Please fill in all required fields');
    }
  };

  const themeClasses = {
    bg: darkMode ? 'bg-gray-900' : 'bg-[#D6CDB8]',
    cardBg: darkMode ? 'bg-gray-800' : 'bg-white',
    text: darkMode ? 'text-white' : 'text-[#222222]',
    textMuted: darkMode ? 'text-gray-400' : 'text-[#222222]',
    input: darkMode 
      ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400 focus:ring-[#3E5641] focus:border-[#3E5641]' 
      : 'bg-white border-gray-300 text-[#222222] placeholder-gray-500 focus:ring-[#3E5641] focus:border-[#3E5641]',
    button: darkMode 
      ? 'bg-white text-gray-900 hover:bg-gray-100' 
      : 'bg-[#3E5641] text-white hover:bg-[#2D3F2F]'
  };

  return (
    <div className={`min-h-screen ${themeClasses.bg} flex items-center justify-center px-6 py-8`} style={{ fontFamily: 'Nunito, sans-serif' }}>
      <div className="w-full max-w-md">
        <button
          onClick={() => navigate('/')}
          className="text-gray-600 hover:text-gray-800 mb-8 flex items-center gap-2 text-base transition-colors"
        >
          <ArrowLeft size={20} />
          Back
        </button>
        
        <div className={`${themeClasses.cardBg} rounded-xl p-8 shadow-lg`}>
          <div className="text-center mb-8">
            <div className={`text-3xl font-bold ${themeClasses.text} mb-2`}>
              <span className="relative">
                h<span className="absolute -top-1 -right-1 text-[#3E5641] text-lg">🌿</span>arv
              </span>
            </div>
            <h1 className={`text-2xl font-semibold ${themeClasses.text} mb-2`}>Create Your Account</h1>
            <p className={`text-base ${themeClasses.textMuted}`}>Join the Primer Initiative learning experience</p>
          </div>

          <div className="space-y-6">
            <div className="space-y-4">
              <h3 className={`text-lg font-semibold ${themeClasses.text} mb-4`}>Account Information</h3>
              
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Full Name"
                className={`w-full px-4 py-4 border rounded-lg text-base focus:outline-none focus:ring-2 ${themeClasses.input}`}
              />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Email Address"
                className={`w-full px-4 py-4 border rounded-lg text-base focus:outline-none focus:ring-2 ${themeClasses.input}`}
              />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Password"
                className={`w-full px-4 py-4 border rounded-lg text-base focus:outline-none focus:ring-2 ${themeClasses.input}`}
              />
            </div>

            <div className="space-y-4 pt-6 border-t border-gray-200 dark:border-gray-600">
              <h3 className={`text-lg font-semibold ${themeClasses.text} mb-4`}>Learning Profile</h3>
              
              <textarea
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder="Why are you taking this mass communication course?"
                className={`w-full px-4 py-4 border rounded-lg text-base focus:outline-none focus:ring-2 resize-none ${themeClasses.input}`}
                rows="3"
              />
              <select
                value={familiarity}
                onChange={(e) => setFamiliarity(e.target.value)}
                className={`w-full px-4 py-4 border rounded-lg text-base focus:outline-none focus:ring-2 ${themeClasses.input}`}
              >
                <option value="">How familiar are you with mass communication?</option>
                <option value="Not at all familiar">Not at all familiar</option>
                <option value="Somewhat familiar">Somewhat familiar</option>
                <option value="Very familiar">Very familiar</option>
                <option value="Expert level">Expert level</option>
              </select>
              <select
                value={learningStyle}
                onChange={(e) => setLearningStyle(e.target.value)}
                className={`w-full px-4 py-4 border rounded-lg text-base focus:outline-none focus:ring-2 ${themeClasses.input}`}
              >
                <option value="">What's your preferred learning style?</option>
                <option value="Visual learner">Visual learner</option>
                <option value="Auditory learner">Auditory learner</option>
                <option value="Kinesthetic learner">Kinesthetic learner</option>
                <option value="Reading/writing learner">Reading/writing learner</option>
              </select>
              <textarea
                value={goals}
                onChange={(e) => setGoals(e.target.value)}
                placeholder="What do you hope to achieve in this course?"
                className={`w-full px-4 py-4 border rounded-lg text-base focus:outline-none focus:ring-2 resize-none ${themeClasses.input}`}
                rows="3"
              />
            </div>

            <button
              onClick={handleSubmit}
              disabled={loading}
              className={`w-full py-4 rounded-lg text-lg font-semibold transition-colors disabled:opacity-50 flex items-center justify-center ${themeClasses.button}`}
            >
              {loading ? <Loader2 className="animate-spin mr-2" size={20} /> : null}
              {loading ? 'Creating Account...' : 'Create Account'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Dashboard Component
const Dashboard = () => {
  const [darkMode, setDarkMode] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [completedModules] = useState(new Set([0, 1, 2]));

  const modules = [
    "Introduction to Mass Communication",
    "History and Evolution of Media",
    "Media Theory and Effects",
    "Print Media and Journalism",
    "Broadcasting: Radio and Television",
    "Digital Media and the Internet",
    "Social Media and New Platforms",
    "Media Ethics and Responsibility",
    "Media Law and Regulation",
    "Advertising and Public Relations",
    "Media Economics and Business Models",
    "Global Media and Cultural Impact",
    "Media Literacy and Critical Analysis",
    "Future of Mass Communication",
    "Capstone: Integrating Knowledge"
  ];

  const handleModuleSelect = (moduleTitle, index) => {
    navigate(`/module/${index + 1}`);
  };

  const handleFAQ = () => {
    navigate('/faq');
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const themeClasses = {
    bg: darkMode ? 'bg-gray-900' : 'bg-[#D6CDB8]',
    cardBg: darkMode ? 'bg-gray-800' : 'bg-white',
    text: darkMode ? 'text-white' : 'text-[#222222]',
    textMuted: darkMode ? 'text-gray-400' : 'text-[#222222]',
    border: darkMode ? 'border-gray-700' : 'border-gray-200',
    moduleCard: darkMode ? 'bg-gray-800 hover:bg-gray-700' : 'bg-white hover:bg-gray-50'
  };

  return (
    <div className={`min-h-screen ${themeClasses.bg}`} style={{ fontFamily: 'Nunito, sans-serif' }}>
      <div className={`${themeClasses.cardBg} border-b ${themeClasses.border} shadow-sm`}>
        <div className="max-w-6xl mx-auto px-8 py-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className={`text-2xl font-bold ${themeClasses.text}`}>
              <span className="relative">
                h<span className="absolute -top-1 -right-1 text-[#3E5641] text-sm">🌿</span>arv
              </span>
            </div>
            <span className={`font-semibold text-xl ${themeClasses.text}`}>Primer Initiative</span>
          </div>
          <div className="flex items-center gap-6">
            <div className={`flex items-center gap-3 text-base ${themeClasses.textMuted}`}>
              <User size={18} />
              {user?.name || 'Student'}
            </div>
            <button
              onClick={handleLogout}
              className={`text-base text-gray-500 hover:text-gray-700 flex items-center gap-2 transition-colors`}
            >
              <LogOut size={18} />
              Sign out
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-8 py-12">
        <div className="mb-12">
          <h1 className={`text-3xl font-semibold ${themeClasses.text} mb-3`}>
            Welcome, {user?.name?.split(' ')[0] || 'Student'}
          </h1>
          <p className={`text-lg ${themeClasses.textMuted}`}>
            Continue your mass communication learning journey
          </p>
        </div>

        <div className="mb-12 flex items-center gap-8">
          <div className="flex items-center gap-3">
            <div className="w-4 h-4 bg-[#3E5641] rounded-full"></div>
            <span className={`text-lg ${themeClasses.textMuted} font-medium`}>
              {completedModules.size} of {modules.length} modules completed
            </span>
          </div>
          <div className={`text-base text-gray-500`}>
            {Math.round((completedModules.size / modules.length) * 100)}% Progress
          </div>
        </div>

        <div className="mb-12">
          <h2 className={`text-2xl font-semibold ${themeClasses.text} mb-8`}>Course Modules</h2>
          <div className="space-y-3">
            {modules.map((title, index) => {
              const isCompleted = completedModules.has(index);
              return (
                <button
                  key={index}
                  onClick={() => handleModuleSelect(title, index)}
                  className={`w-full text-left p-6 rounded-xl ${themeClasses.moduleCard} transition-all shadow-sm border ${themeClasses.border} group`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-4">
                        <span className={`text-lg text-gray-500 font-bold font-mono w-12`}>
                          {String(index + 1).padStart(2, '0')}
                        </span>
                        {isCompleted && (
                          <div className="w-3 h-3 bg-[#3E5641] rounded-full"></div>
                        )}
                      </div>
                      <div>
                        <h3 className={`text-lg font-semibold ${themeClasses.text} transition-colors ${isCompleted ? 'opacity-75' : ''}`}>
                          {title}
                        </h3>
                        <p className={`text-base text-gray-500 mt-1`}>
                          {isCompleted ? 'Completed' : 'Ready to start'}
                        </p>
                      </div>
                    </div>
                    <div className="text-gray-400 group-hover:text-gray-600 transition-colors">
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                        <path d="M9 6l6 6-6 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        <div className="flex gap-6">
          <button
            onClick={handleFAQ}
            className={`flex items-center gap-3 px-6 py-4 rounded-xl ${themeClasses.moduleCard} transition-colors border ${themeClasses.border} shadow-sm`}
          >
            <HelpCircle size={20} className="text-[#3E5641]" />
            <span className={`text-lg font-medium ${themeClasses.text}`}>FAQ & Help</span>
          </button>
        </div>
      </div>
    </div>
  );
};

// Module Page Component
const ModulePage = () => {
  const [darkMode, setDarkMode] = useState(false);
  const { id } = useParams();
  const navigate = useNavigate();
  const [currentConversationId, setCurrentConversationId] = useState(1);
  const [conversations, setConversations] = useState({
    1: {
      id: 1,
      title: "Understanding Media Influence",
      messages: [
        {
          role: 'assistant',
          content: `Hello! I'm Harv, your Socratic tutor for Module ${id}. Instead of giving you direct answers, I'll guide you to discover insights through thoughtful questions.\n\nWhat aspects of this module's content are you most curious about?`
        }
      ],
      lastActivity: new Date().toISOString()
    }
  });
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [showResources, setShowResources] = useState(true);

  const modules = [
    "Introduction to Mass Communication",
    "History and Evolution of Media",
    "Media Theory and Effects",
    "Print Media and Journalism",
    "Broadcasting: Radio and Television",
    "Digital Media and the Internet",
    "Social Media and New Platforms",
    "Media Ethics and Responsibility",
    "Media Law and Regulation",
    "Advertising and Public Relations",
    "Media Economics and Business Models",
    "Global Media and Cultural Impact",
    "Media Literacy and Critical Analysis",
    "Future of Mass Communication",
    "Capstone: Integrating Knowledge"
  ];

  const module = {
    id: parseInt(id),
    title: modules[parseInt(id) - 1] || "Module",
    resources: [
      { title: "Lecture Slides: Core Concepts", type: "slides", url: "#" },
      { title: "Reading: Essential Theory", type: "reading", url: "#" },
      { title: "Case Study: Real-World Application", type: "reading", url: "#" },
      { title: "Video: Expert Perspectives", type: "video", url: "#" }
    ]
  };

  const sendMessage = () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    const updatedConversations = {
      ...conversations,
      [currentConversationId]: {
        ...conversations[currentConversationId],
        messages: [...conversations[currentConversationId].messages, userMessage],
        lastActivity: new Date().toISOString()
      }
    };
    setConversations(updatedConversations);
    setInput('');
    setLoading(true);

    setTimeout(() => {
      const responses = [
        "That's an insightful observation! What evidence have you seen that supports this perspective?",
        "Excellent question! What's your initial thinking on this? What patterns have you noticed?",
        "You're making important connections. How might this apply in different contexts?",
        "That's thoughtful. What questions does this raise for you about media responsibility?",
        "I can see you're thinking deeply. What counterarguments might someone present?",
        "Very perceptive! How has this evolved with digital media?",
        "Interesting perspective! What led you to that conclusion?"
      ];
      
      const randomResponse = responses[Math.floor(Math.random() * responses.length)];
      const assistantMessage = { role: 'assistant', content: randomResponse };

      setConversations(prev => ({
        ...prev,
        [currentConversationId]: {
          ...prev[currentConversationId],
          messages: [...prev[currentConversationId].messages, assistantMessage],
          lastActivity: new Date().toISOString()
        }
      }));
      setLoading(false);
    }, 1500);
  };

  const createNewConversation = () => {
    const newId = Math.max(...Object.keys(conversations).map(Number)) + 1;
    const newConversation = {
      id: newId,
      title: "New Conversation",
      messages: [
        {
          role: 'assistant',
          content: `Hello! I'm Harv, ready to explore ${module.title} with you through thoughtful dialogue. What would you like to discuss today?`
        }
      ],
      lastActivity: new Date().toISOString()
    };

    setConversations(prev => ({
      ...prev,
      [newId]: newConversation
    }));
    setCurrentConversationId(newId);
  };

  const exportChat = () => {
    const currentConversation = conversations[currentConversationId];
    const chatText = currentConversation.messages.map(msg =>
      `${msg.role === 'user' ? 'Student' : 'Harv'}: ${msg.content}`
    ).join('\n\n');

    const blob = new Blob([chatText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `module-${module.id}-conversation.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleFilesUploaded = (files) => {
    alert(`Uploaded ${files.length} file(s) to module resources!`);
  };

  const themeClasses = {
    bg: darkMode ? 'bg-gray-900' : 'bg-[#D6CDB8]',
    cardBg: darkMode ? 'bg-gray-800' : 'bg-white',
    text: darkMode ? 'text-white' : 'text-[#222222]',
    textMuted: darkMode ? 'text-gray-400' : 'text-[#222222]',
    border: darkMode ? 'border-gray-700' : 'border-gray-200',
    input: darkMode 
      ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400 focus:ring-[#3E5641] focus:border-[#3E5641]' 
      : 'bg-white border-gray-300 text-[#222222] placeholder-gray-500 focus:ring-[#3E5641] focus:border-[#3E5641]',
    button: darkMode 
      ? 'bg-white text-gray-900 hover:bg-gray-100' 
      : 'bg-[#3E5641] text-white hover:bg-[#2D3F2F]',
    avatar: darkMode ? 'bg-gray-700 text-gray-300' : 'bg-gray-100 text-[#222222]',
    hover: darkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-50'
  };

  const currentConversation = conversations[currentConversationId];

  return (
    <div className={`min-h-screen ${themeClasses.bg} flex`} style={{ fontFamily: 'Nunito, sans-serif' }}>
      {showResources && (
        <div className={`w-80 ${themeClasses.cardBg} border-r ${themeClasses.border} flex flex-col shadow-lg`}>
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className={`font-semibold ${themeClasses.text} text-lg mb-4`}>
              Module Resources
            </h2>
            <button
              onClick={createNewConversation}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl ${themeClasses.border} border ${themeClasses.hover} transition-colors text-base ${themeClasses.textMuted} font-medium mb-6`}
            >
              <Plus size={18} />
              New Conversation
            </button>

            <DragDropUpload 
              onFilesUploaded={handleFilesUploaded}
              accept=".pdf,.doc,.docx,.ppt,.pptx"
              className="mb-6"
            />
          </div>

          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <h3 className={`font-semibold ${themeClasses.text} mb-4 text-base`}>Lecture Materials</h3>
            <div className="space-y-2">
              {module.resources.map((resource, index) => (
                <button
                  key={index}
                  onClick={() => alert(`Opening: ${resource.title}`)}
                  className={`w-full text-left p-3 rounded-lg ${themeClasses.hover} transition-colors group`}
                >
                  <div className="flex items-center gap-3">
                    <Monitor size={16} className="text-[#3E5641]" />
                    <span className={`text-sm font-medium ${themeClasses.text} transition-colors`}>
                      {resource.title}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-4">
            <h3 className={`font-semibold ${themeClasses.text} mb-4 text-base`}>Your Conversations</h3>
            {Object.values(conversations).map((conversation) => (
              <button
                key={conversation.id}
                onClick={() => setCurrentConversationId(conversation.id)}
                className={`w-full text-left p-4 rounded-xl mb-3 transition-colors border ${
                  conversation.id === currentConversationId
                    ? 'bg-[#3E5641] bg-opacity-10 border-[#3E5641]'
                    : `${themeClasses.hover} border-transparent`
                }`}
              >
                <div className="flex items-center gap-2 mb-2">
                  <MessageSquare size={16} className={themeClasses.textMuted} />
                  <span className={`text-base font-semibold ${themeClasses.text} truncate`}>
                    {conversation.title}
                  </span>
                </div>
                <span className={`text-sm text-gray-500`}>
                  {conversation.messages.length} messages
                </span>
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="flex-1 flex flex-col">
        <div className={`${themeClasses.cardBg} border-b ${themeClasses.border} px-8 py-6 shadow-sm`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              <button
                onClick={() => navigate('/dashboard')}
                className="text-gray-500 hover:text-gray-700 flex items-center gap-2 text-base transition-colors"
              >
                <ArrowLeft size={20} />
                Back to Dashboard
              </button>
              <div>
                <h1 className={`font-semibold ${themeClasses.text} text-xl`}>
                  {module.title}
                </h1>
                <p className={`text-base text-gray-500 mt-1`}>
                  Harv Chat: {currentConversation.title}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <button
                onClick={() => setShowResources(!showResources)}
                className={`p-3 rounded-lg text-gray-500 hover:text-gray-700 transition-colors`}
              >
                <BookOpen size={20} />
              </button>
              <button
                onClick={exportChat}
                className="text-base text-gray-500 hover:text-gray-700 flex items-center gap-2 transition-colors px-4 py-2 rounded-lg hover:bg-gray-50"
              >
                <Download size={16} />
                Export
              </button>
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto">
          <div className="max-w-4xl mx-auto px-8 py-8">
            <div className="space-y-8">
              {currentConversation.messages.map((message, index) => (
                <div key={index} className="flex gap-6">
                  <div className={`w-10 h-10 rounded-full ${themeClasses.avatar} flex items-center justify-center flex-shrink-0 mt-1 font-semibold`}>
                    <span className="text-base">
                      {message.role === 'user' ? 'Y' : 'H'}
                    </span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className={`text-base ${themeClasses.text} leading-relaxed whitespace-pre-wrap`}>
                      {message.content}
                    </div>
                  </div>
                </div>
              ))}

              {loading && (
                <div className="flex gap-6">
                  <div className={`w-10 h-10 rounded-full ${themeClasses.avatar} flex items-center justify-center flex-shrink-0 mt-1 font-semibold`}>
                    <span className="text-base">H</span>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 text-base text-gray-500">
                      <Loader2 size={18} className="animate-spin" />
                      Harv is thinking...
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className={`${themeClasses.cardBg} border-t ${themeClasses.border} px-8 py-6`}>
          <div className="max-w-4xl mx-auto">
            <div className="flex gap-4 items-end">
              <div className="flex-1">
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), sendMessage())}
                  placeholder="Share your thoughts or ask a question..."
                  className={`w-full px-4 py-4 border rounded-xl text-base resize-none focus:outline-none focus:ring-2 ${themeClasses.input}`}
                  rows="2"
                  disabled={loading}
                />
              </div>
              <button
                onClick={sendMessage}
                disabled={loading || !input.trim()}
                className={`w-12 h-12 rounded-xl flex items-center justify-center transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${themeClasses.button} shadow-sm`}
              >
                <Send size={20} />
              </button>
            </div>
            <div className="flex items-center justify-between mt-3">
              <p className="text-sm text-gray-500">
                Press Enter to send, Shift+Enter for new line
              </p>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-[#3E5641] rounded-full"></div>
                <span className="text-sm text-gray-500">
                  {currentConversation.messages.filter(m => m.role === 'user').length} messages sent
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// FAQ Page Component
const FAQPage = () => {
  const [darkMode, setDarkMode] = useState(false);
  const [openFAQ, setOpenFAQ] = useState(null);
  const navigate = useNavigate();

  const faqs = [
    {
      question: "How do I start a conversation with Harv?",
      answer: "Simply select any module from your dashboard and click to open it. Harv will greet you and begin the Socratic dialogue immediately. You can start multiple conversations per module to explore different topics."
    },
    {
      question: "What is Socratic learning and how does it work?",
      answer: "Socratic learning is a method where Harv guides your understanding through thoughtful questions rather than giving direct answers. This helps you discover insights through dialogue, think critically, and develop deeper comprehension of mass communication concepts."
    },
    {
      question: "How do I upload and manage files?",
      answer: "Use the drag-and-drop area in each module's resource sidebar. You can drag files directly into the upload zone or click to browse and select files. Supported formats include PDF, DOC, DOCX, PPT, and PPTX."
    },
    {
      question: "How do I export my chat logs?",
      answer: "In any module chat interface, click the 'Export' button in the top right corner. This downloads your conversation as a text file for submission to your instructor or for your personal records."
    },
    {
      question: "Can I have multiple conversations per module?",
      answer: "Yes! Each module supports multiple distinct conversations. Click 'New Conversation' in the module interface to start fresh discussions on different aspects of the module content."
    }
  ];

  const themeClasses = {
    bg: darkMode ? 'bg-gray-900' : 'bg-[#D6CDB8]',
    cardBg: darkMode ? 'bg-gray-800' : 'bg-white',
    text: darkMode ? 'text-white' : 'text-[#222222]',
    textMuted: darkMode ? 'text-gray-400' : 'text-[#222222]',
    border: darkMode ? 'border-gray-700' : 'border-gray-200',
    hover: darkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-50',
    button: darkMode 
      ? 'bg-white text-gray-900 hover:bg-gray-100' 
      : 'bg-[#3E5641] text-white hover:bg-[#2D3F2F]'
  };

  return (
    <div className={`min-h-screen ${themeClasses.bg}`} style={{ fontFamily: 'Nunito, sans-serif' }}>
      <div className={`${themeClasses.cardBg} border-b ${themeClasses.border} px-8 py-6 shadow-sm`}>
        <button
          onClick={() => navigate('/dashboard')}
          className="text-gray-500 hover:text-gray-700 flex items-center gap-2 text-base transition-colors"
        >
          <ArrowLeft size={20} />
          Back to Dashboard
        </button>
      </div>

      <div className="max-w-4xl mx-auto px-8 py-12">
        <div className="mb-12">
          <h1 className={`text-3xl font-semibold ${themeClasses.text} mb-3`}>Help & FAQ</h1>
          <p className={`text-lg ${themeClasses.textMuted}`}>
            Common questions about using the Primer Initiative platform
          </p>
        </div>

        <div className="space-y-2 mb-12">
          {faqs.map((faq, index) => (
            <div key={index} className={`${themeClasses.cardBg} border ${themeClasses.border} rounded-xl shadow-sm`}>
              <button
                onClick={() => setOpenFAQ(openFAQ === index ? null : index)}
                className={`w-full text-left px-6 py-5 flex items-center justify-between ${themeClasses.hover} transition-colors rounded-xl`}
              >
                <span className={`text-lg font-semibold ${themeClasses.text} pr-4`}>
                  {faq.question}
                </span>
                <ChevronDown
                  size={20}
                  className={`text-gray-500 transition-transform flex-shrink-0 ${
                    openFAQ === index ? 'rotate-180' : ''
                  }`}
                />
              </button>
              {openFAQ === index && (
                <div className={`px-6 pb-6 border-t ${themeClasses.border}`}>
                  <p className={`text-base ${themeClasses.textMuted} leading-relaxed pt-4`}>
                    {faq.answer}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>

        <div className={`${themeClasses.cardBg} rounded-xl p-8 shadow-sm border ${themeClasses.border}`}>
          <h2 className={`text-xl font-semibold ${themeClasses.text} mb-3`}>
            Still need help?
          </h2>
          <p className={`text-base ${themeClasses.textMuted} mb-6 leading-relaxed`}>
            If you can't find the answer you're looking for, our support team is here to help.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4">
            <button
              onClick={() => alert('Contact instructor feature would open')}
              className={`flex items-center gap-3 px-6 py-4 rounded-xl ${themeClasses.button} transition-colors shadow-sm font-semibold`}
            >
              <Mail size={20} />
              Contact Instructor
            </button>
            
            <button
              onClick={() => alert('Technical support feature would open')}
              className={`flex items-center gap-3 px-6 py-4 rounded-xl border-2 ${themeClasses.border} ${themeClasses.hover} transition-colors font-semibold ${themeClasses.text}`}
            >
              <MessageCircle size={20} />
              Technical Support
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Main App Component
const App = () => {
  return (
    <AuthProvider>
      <Router>
        <div style={{ fontFamily: 'Nunito, sans-serif' }}>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
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
            <Route path="/faq" element={<FAQPage />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
};

export default App;
