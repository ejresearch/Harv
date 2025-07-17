#!/bin/bash
# Demo Mode Setup - Test Your Configured Modules
# Creates a simple frontend that connects to your configured backend
# Run from harv root directory: bash demo_mode_setup.sh

echo "🎮 DEMO MODE SETUP - Test Your Configured Modules"
echo "================================================="

# Create demo frontend directory
echo "📁 Creating demo frontend..."
mkdir -p demo_frontend
cd demo_frontend

# Create package.json for simple React setup
cat > package.json << 'EOF'
{
  "name": "harv-demo",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build"
  },
  "browserslist": {
    "production": [">0.2%", "not dead", "not op_mini all"],
    "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
  }
}
EOF

# Create public directory
mkdir -p public
cat > public/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Harv Demo - Test Your Modules</title>
    <style>
      body { margin: 0; font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
    </style>
  </head>
  <body>
    <div id="root"></div>
  </body>
</html>
EOF

# Create src directory
mkdir -p src

# Create main App.js - connects to your backend
cat > src/App.js << 'EOF'
import React, { useState, useEffect } from 'react';
import './App.css';

// Your backend URL
const BACKEND_URL = 'http://127.0.0.1:8000';

function App() {
  const [modules, setModules] = useState([]);
  const [currentView, setCurrentView] = useState('modules');
  const [selectedModule, setSelectedModule] = useState(null);
  const [loading, setLoading] = useState(true);

  // Load modules from your actual backend
  useEffect(() => {
    loadModules();
  }, []);

  const loadModules = async () => {
    try {
      console.log('🔍 Loading modules from backend...');
      const response = await fetch(`${BACKEND_URL}/modules`);
      
      if (response.ok) {
        const moduleData = await response.json();
        setModules(moduleData);
        console.log(`✅ Loaded ${moduleData.length} modules from your backend`);
        setLoading(false);
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      console.error('❌ Failed to load modules:', error);
      console.log('💡 Make sure your backend is running: cd backend && uvicorn app.main:app --reload');
      
      // Fallback demo modules
      setModules([
        { id: 1, title: "Backend Not Connected", description: "Start your backend to see real modules" }
      ]);
      setLoading(false);
    }
  };

  const startModule = async (module) => {
    console.log(`🚀 Starting module: ${module.title}`);
    
    // Try to load module configuration from your backend
    try {
      const configResponse = await fetch(`${BACKEND_URL}/modules/${module.id}/config`);
      if (configResponse.ok) {
        const config = await configResponse.json();
        console.log(`🔧 Loaded module configuration:`, config);
        console.log(`📚 Memory prompt: ${config.module_prompt?.substring(0, 100)}...`);
      }
    } catch (error) {
      console.log(`⚠️ No configuration found for module ${module.id}`);
    }
    
    setSelectedModule(module);
    setCurrentView('chat');
  };

  const backToModules = () => {
    setCurrentView('modules');
    setSelectedModule(null);
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="logo">harv 🌱</div>
        <p>Connecting to your backend...</p>
      </div>
    );
  }

  if (currentView === 'modules') {
    return (
      <div className="app">
        <header className="header">
          <div className="logo">harv 🌱</div>
          <div className="subtitle">Demo Mode - Test Your Configured Modules</div>
        </header>

        <main className="main">
          <div className="hero">
            <h1>Test Your Memory Configuration</h1>
            <p>Configure modules in GUI → Test here immediately</p>
            <div className="workflow">
              <span className="step">1. Configure in GUI</span>
              <span className="arrow">→</span>
              <span className="step">2. Test here</span>
              <span className="arrow">→</span>
              <span className="step">3. See AI responses</span>
            </div>
          </div>

          <div className="modules-grid">
            {modules.map((module) => (
              <div
                key={module.id}
                className="module-card"
                onClick={() => startModule(module)}
              >
                <h3>{module.title}</h3>
                <p>{module.description || 'Mass Communication Module'}</p>
                <div className="module-meta">
                  <span>Module {module.id}</span>
                  <span className="test-badge">Test Ready</span>
                </div>
              </div>
            ))}
          </div>

          <div className="instructions">
            <h3>🔧 Development Workflow</h3>
            <ol>
              <li><strong>Configure:</strong> Open <code>http://localhost:3000/dev-gui.html</code></li>
              <li><strong>Edit Memory:</strong> Set Socratic prompts, memory rules, learning styles</li>
              <li><strong>Save:</strong> Click save in GUI</li>
              <li><strong>Test:</strong> Click module here to test AI responses immediately</li>
            </ol>
          </div>
        </main>
      </div>
    );
  }

  if (currentView === 'chat') {
    return <ChatInterface module={selectedModule} onBack={backToModules} />;
  }
}

// Chat interface component
function ChatInterface({ module, onBack }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);

  useEffect(() => {
    // Initial message shows module configuration is active
    setMessages([{
      role: 'assistant',
      content: `Welcome! I'm Harv, your Socratic tutor for ${module.title}. 

I'm using the memory configuration you set in the GUI. Rather than giving direct answers, I'll guide you through thoughtful questions based on your configured prompts.

What would you like to explore first?`,
      timestamp: Date.now()
    }]);
  }, [module]);

  const sendMessage = async () => {
    if (!input.trim() || sending) return;

    const userMessage = { 
      role: 'user', 
      content: input, 
      timestamp: Date.now() 
    };
    
    setMessages(prev => [...prev, userMessage]);
    const messageText = input;
    setInput('');
    setSending(true);

    try {
      console.log(`💬 Sending message to module ${module.id}: "${messageText}"`);
      
      const response = await fetch(`${BACKEND_URL}/chat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 999, // Demo user
          module_id: module.id,
          message: messageText,
          conversation_id: 'demo'
        })
      });

      if (response.ok) {
        const data = await response.json();
        console.log(`✅ AI Response received: "${data.reply?.substring(0, 50)}..."`);
        console.log(`🧠 Memory context: Conversation ${data.conversation_id}`);
        
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: data.reply,
          timestamp: Date.now(),
          conversationId: data.conversation_id
        }]);
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      console.error('❌ Chat error:', error);
      
      // Fallback response
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: "I'm having trouble connecting to the AI system right now. What aspects of this topic are you most curious about?",
        timestamp: Date.now(),
        error: true
      }]);
    }

    setSending(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chat-container">
      <header className="chat-header">
        <div className="chat-title">
          <h2>{module.title}</h2>
          <p>Testing your GUI configuration • Module {module.id}</p>
        </div>
        <button className="back-button" onClick={onBack}>
          ← Back to Modules
        </button>
      </header>

      <div className="chat-messages">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            <div className="message-content">{message.content}</div>
            {message.conversationId && (
              <div className="message-meta">
                Conversation {message.conversationId} • Memory active
              </div>
            )}
            {message.error && (
              <div className="message-meta error">
                Fallback response • Check backend connection
              </div>
            )}
          </div>
        ))}
        {sending && (
          <div className="message assistant">
            <div className="message-content">
              <div className="typing">Harv is thinking...</div>
            </div>
          </div>
        )}
      </div>

      <div className="chat-input-area">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask about this module's topic..."
          className="chat-input"
          rows="2"
        />
        <button 
          onClick={sendMessage} 
          disabled={!input.trim() || sending}
          className="send-button"
        >
          {sending ? 'Sending...' : 'Send'}
        </button>
      </div>
    </div>
  );
}

export default App;
EOF

# Create CSS styling
cat > src/App.css << 'EOF'
/* Harv Demo Styling */
:root {
  --primary-green: #3E5641;
  --beige-bg: #D6CDB8;
  --soft-beige: #F5F2EA;
  --standard-black: #222222;
  --accent-white: #FFFFFF;
  --light-gray: #F8F9FA;
  --border-light: #E9ECEF;
  --text-muted: #6C757D;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  background: var(--soft-beige);
  color: var(--standard-black);
  line-height: 1.6;
}

.app {
  min-height: 100vh;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  gap: 1rem;
}

.logo {
  font-size: 2rem;
  font-weight: 700;
  color: var(--primary-green);
}

.header {
  background: var(--accent-white);
  padding: 1rem 2rem;
  border-bottom: 1px solid var(--border-light);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.subtitle {
  color: var(--text-muted);
  font-size: 0.9rem;
}

.main {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.hero {
  text-align: center;
  margin-bottom: 3rem;
}

.hero h1 {
  font-size: 2.5rem;
  color: var(--primary-green);
  margin-bottom: 1rem;
}

.hero p {
  font-size: 1.2rem;
  color: var(--text-muted);
  margin-bottom: 2rem;
}

.workflow {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin: 2rem 0;
}

.step {
  background: var(--primary-green);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.9rem;
}

.arrow {
  color: var(--primary-green);
  font-weight: bold;
}

.modules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.module-card {
  background: var(--accent-white);
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid var(--border-light);
  cursor: pointer;
  transition: all 0.2s ease;
}

.module-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(62, 86, 65, 0.1);
  border-color: var(--primary-green);
}

.module-card h3 {
  color: var(--primary-green);
  margin-bottom: 0.5rem;
  font-size: 1.2rem;
}

.module-card p {
  color: var(--text-muted);
  margin-bottom: 1rem;
  font-size: 0.95rem;
}

.module-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8rem;
  color: var(--text-muted);
}

.test-badge {
  background: var(--beige-bg);
  color: var(--primary-green);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-weight: 500;
}

.instructions {
  background: var(--accent-white);
  padding: 2rem;
  border-radius: 12px;
  border: 1px solid var(--border-light);
}

.instructions h3 {
  color: var(--primary-green);
  margin-bottom: 1rem;
}

.instructions ol {
  margin: 0;
  padding-left: 1.5rem;
}

.instructions li {
  margin-bottom: 0.5rem;
}

.instructions code {
  background: var(--light-gray);
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-size: 0.9rem;
}

/* Chat Interface */
.chat-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.chat-header {
  background: var(--primary-green);
  color: white;
  padding: 1.5rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-title h2 {
  margin: 0 0 0.25rem 0;
}

.chat-title p {
  margin: 0;
  opacity: 0.8;
  font-size: 0.9rem;
}

.back-button {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
}

.back-button:hover {
  background: rgba(255, 255, 255, 0.3);
}

.chat-messages {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message {
  max-width: 80%;
  padding: 1rem 1.25rem;
  border-radius: 16px;
  font-size: 0.95rem;
  line-height: 1.5;
}

.message.user {
  background: var(--beige-bg);
  color: var(--standard-black);
  align-self: flex-end;
  border-bottom-right-radius: 4px;
}

.message.assistant {
  background: var(--primary-green);
  color: var(--accent-white);
  align-self: flex-start;
  border-bottom-left-radius: 4px;
}

.message-meta {
  font-size: 0.75rem;
  opacity: 0.7;
  margin-top: 0.5rem;
}

.message-meta.error {
  color: #ff6b6b;
}

.typing {
  opacity: 0.7;
  font-style: italic;
}

.chat-input-area {
  padding: 1.5rem;
  border-top: 1px solid var(--border-light);
  background: var(--light-gray);
  display: flex;
  gap: 0.75rem;
  align-items: flex-end;
}

.chat-input {
  flex: 1;
  border: 1px solid var(--border-light);
  border-radius: 8px;
  padding: 0.75rem 1rem;
  font-size: 0.95rem;
  font-family: inherit;
  resize: none;
  background: var(--accent-white);
}

.chat-input:focus {
  outline: none;
  border-color: var(--primary-green);
  box-shadow: 0 0 0 3px rgba(62, 86, 65, 0.1);
}

.send-button {
  background: var(--primary-green);
  color: var(--accent-white);
  border: none;
  border-radius: 8px;
  padding: 0.75rem 1.5rem;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s ease;
  min-height: 44px;
}

.send-button:hover:not(:disabled) {
  background: #2a3d2b;
}

.send-button:disabled {
  background: var(--text-muted);
  cursor: not-allowed;
}

/* Responsive */
@media (max-width: 768px) {
  .modules-grid {
    grid-template-columns: 1fr;
  }
  
  .hero h1 {
    font-size: 2rem;
  }
  
  .workflow {
    flex-direction: column;
  }
  
  .main {
    padding: 1rem;
  }
  
  .chat-header {
    padding: 1rem;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}
EOF

# Create index.js
cat > src/index.js << 'EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
EOF

cd .. # Back to harv root

# Create startup script
cat > start_demo.sh << 'EOF'
#!/bin/bash
# Start Demo Mode - Test Your Configured Modules
echo "🎮 STARTING HARV DEMO MODE"
echo "=========================="

# Check if backend is running
echo "🔍 Checking backend..."
if curl -s http://127.0.0.1:8000/health > /dev/null; then
    echo "✅ Backend is running"
else
    echo "⚠️  Backend not detected - starting it..."
    cd backend
    uvicorn app.main:app --reload &
    BACKEND_PID=$!
    cd ..
    echo "✅ Backend started (PID: $BACKEND_PID)"
    sleep 3
fi

# Check if GUI is running
echo "🔍 Checking GUI..."
if curl -s http://localhost:3000/dev-gui.html > /dev/null; then
    echo "✅ GUI is running"
else
    echo "⚠️  GUI not detected - starting it..."
    cd tools
    python3 -m http.server 3000 &
    GUI_PID=$!
    cd ..
    echo "✅ GUI started (PID: $GUI_PID)"
    sleep 2
fi

# Start demo frontend
echo "🚀 Starting demo frontend..."
cd demo_frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

echo ""
echo "🎉 DEMO MODE READY!"
echo "==================="
echo ""
echo "🔧 Configure: http://localhost:3000/dev-gui.html"
echo "🎮 Test: http://localhost:3000 (will open automatically)"
echo ""
echo "Workflow:"
echo "1. Configure memory/prompts in GUI"
echo "2. Save configuration"
echo "3. Test immediately in demo"
echo "4. See AI responses using your config"
echo ""

# Start React app (will open browser automatically)
npm start
EOF

chmod +x start_demo.sh

echo ""
echo "✅ Demo mode setup complete!"
echo ""
echo "🚀 To start testing your configured modules:"
echo "   bash start_demo.sh"
echo ""
echo "📋 What this gives you:"
echo "   ✅ Simple frontend that loads YOUR modules from backend"
echo "   ✅ Chat interface that uses YOUR memory configuration"
echo "   ✅ Direct connection to your Socratic AI system"
echo "   ✅ No login required - instant testing"
echo ""
echo "🔧 Development workflow:"
echo "   1. Configure modules: http://localhost:3000/dev-gui.html"
echo "   2. Test immediately: Run demo frontend"
echo "   3. See AI responses using your exact configuration"
echo ""
echo "🎯 Ready to test your memory-enhanced modules!"
