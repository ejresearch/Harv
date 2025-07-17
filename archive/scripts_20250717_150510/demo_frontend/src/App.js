// Updated App.js - Claude-style module list
import React, { useState, useEffect } from 'react';
import './App.css';

const BACKEND_URL = 'http://127.0.0.1:8000';

function App() {
  const [modules, setModules] = useState([]);
  const [currentView, setCurrentView] = useState('modules');
  const [selectedModule, setSelectedModule] = useState(null);
  const [loading, setLoading] = useState(true);
  const [backendConnected, setBackendConnected] = useState(false);

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
        setBackendConnected(true);
        console.log(`✅ Loaded ${moduleData.length} modules from your backend`);
        setLoading(false);
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      console.error('❌ Failed to load modules:', error);
      setBackendConnected(false);
      setLoading(false);
    }
  };

  const startModule = async (module) => {
    console.log(`🚀 Starting module: ${module.title}`);
    
    try {
      const configResponse = await fetch(`${BACKEND_URL}/modules/${module.id}/config`);
      if (configResponse.ok) {
        const config = await configResponse.json();
        console.log(`🔧 Loaded module configuration:`, config);
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
      <div className="claude-layout">
        {/* Header */}
        <header className="claude-header">
          <div className="logo">harv 🌱</div>
          <div className="header-status">
            {backendConnected ? (
              <span className="status-connected">✅ Backend Connected</span>
            ) : (
              <span className="status-disconnected">❌ Start Backend</span>
            )}
          </div>
        </header>

        <div className="claude-main">
          {/* Sidebar with module list */}
          <aside className="claude-sidebar">
            <div className="sidebar-header">
              <h3>Communication Modules</h3>
              <span className="module-count">{modules.length} modules</span>
            </div>
            
            <div className="module-list">
              {backendConnected ? (
                modules.map((module) => (
                  <div
                    key={module.id}
                    className="module-item"
                    onClick={() => startModule(module)}
                  >
                    <div className="module-title">{module.title}</div>
                    <div className="module-preview">
                      {module.description?.substring(0, 60) || 'Mass Communication Module'}
                      {module.description?.length > 60 && '...'}
                    </div>
                    <div className="module-meta">
                      <span className="module-id">Module {module.id}</span>
                      <span className="test-status">Test Ready</span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="connection-error">
                  <div className="error-message">
                    <h4>Backend Not Connected</h4>
                    <p>Start your backend to see all 15 modules:</p>
                    <code>cd backend && uvicorn app.main:app --reload</code>
                  </div>
                  
                  {/* Demo module */}
                  <div className="module-item demo">
                    <div className="module-title">Demo Module</div>
                    <div className="module-preview">Start backend to see your real modules</div>
                    <div className="module-meta">
                      <span className="module-id">Demo</span>
                      <span className="test-status disabled">Need Backend</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </aside>

          {/* Main content area */}
          <main className="claude-content">
            <div className="welcome-section">
              <h1>Test Your Memory Configuration</h1>
              <p>Configure modules in GUI → Select module → Test AI responses</p>
              
              <div className="workflow-steps">
                <div className="step">
                  <span className="step-number">1</span>
                  <div className="step-content">
                    <strong>Configure</strong>
                    <p>Open GUI to set memory prompts</p>
                    <a href="http://localhost:3000/dev-gui.html" target="_blank" rel="noopener noreferrer">
                      http://localhost:3000/dev-gui.html
                    </a>
                  </div>
                </div>
                
                <div className="step">
                  <span className="step-number">2</span>
                  <div className="step-content">
                    <strong>Select Module</strong>
                    <p>Click any module in the sidebar to test</p>
                  </div>
                </div>
                
                <div className="step">
                  <span className="step-number">3</span>
                  <div className="step-content">
                    <strong>Test AI</strong>
                    <p>Chat with Harv using your configuration</p>
                  </div>
                </div>
              </div>

              {backendConnected && (
                <div className="module-stats">
                  <div className="stat">
                    <span className="stat-number">{modules.length}</span>
                    <span className="stat-label">Total Modules</span>
                  </div>
                  <div className="stat">
                    <span className="stat-number">{modules.filter(m => m.description).length}</span>
                    <span className="stat-label">Configured</span>
                  </div>
                  <div className="stat">
                    <span className="stat-number">Ready</span>
                    <span className="stat-label">Status</span>
                  </div>
                </div>
              )}
            </div>
          </main>
        </div>
      </div>
    );
  }

  if (currentView === 'chat') {
    return <ChatInterface module={selectedModule} onBack={backToModules} />;
  }
}

// Chat interface component (unchanged)
function ChatInterface({ module, onBack }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);

  useEffect(() => {
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
          user_id: 999,
          module_id: module.id,
          message: messageText,
          conversation_id: 'demo'
        })
      });

      if (response.ok) {
        const data = await response.json();
        console.log(`✅ AI Response: "${data.reply?.substring(0, 50)}..."`);
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
