import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Send, Download, BookOpen, Brain, MessageCircle, User, Bot } from 'lucide-react';
import ApiService from '../services/api';
import { useAuth } from '../context/AuthContext';

const ModulePage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [module, setModule] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const [memoryStats, setMemoryStats] = useState(null);
  const [connected, setConnected] = useState(false);
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    loadModule();
    loadMemoryStats();
    initializeConversation();
  }, [id]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadModule = async () => {
    try {
      const modules = await ApiService.getModules();
      const foundModule = modules.find(m => m.id === parseInt(id));
      setModule(foundModule);
      setConnected(true);
    } catch (error) {
      console.error('Error loading module:', error);
      setConnected(false);
    }
  };

  const loadMemoryStats = async () => {
    try {
      const stats = await ApiService.getMemoryStats(id);
      setMemoryStats(stats);
    } catch (error) {
      console.error('Error loading memory stats:', error);
    }
  };

  const initializeConversation = () => {
    const welcomeMessage = {
      role: 'assistant',
      content: `Welcome! I'm Harv, your Socratic tutor for this module. 🌱

Rather than giving you direct answers, I'll guide you through thoughtful questions to help you discover concepts yourself.

Your learning context is being assembled from:
• Your learning profile and preferences  
• Previous conversations and insights
• Module-specific knowledge base
• Real-time conversation analysis

What would you like to explore first? I'm here to ask the right questions to spark your understanding!`,
      timestamp: new Date().toISOString()
    };
    
    setMessages([welcomeMessage]);
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || loading) return;

    const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      const response = await ApiService.sendMessage({
        user_id: user?.id || 1,
        module_id: parseInt(id),
        message: inputMessage,
        conversation_id: conversationId || 'default'
      });

      const assistantMessage = {
        role: 'assistant',
        content: response.reply || response.response || "That's interesting! What led you to think about it that way?",
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }

    } catch (error) {
      console.error('Error sending message:', error);
      
      // Graceful fallback with Socratic responses
      const fallbackResponses = [
        "That's fascinating! What led you to think about it that way?",
        "I'm curious about your perspective. Can you break that down for me?",
        "What examples from your experience might relate to this?",
        "What questions does this raise for you about communication?",
        "How might this concept apply in different contexts?"
      ];
      
      const errorMessage = {
        role: 'assistant',
        content: fallbackResponses[Math.floor(Math.random() * fallbackResponses.length)],
        timestamp: new Date().toISOString()
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

  const exportConversation = async () => {
    try {
      const response = await ApiService.exportConversation({
        conversation_id: conversationId || 'default',
        format: 'txt'
      });
      
      // Create download
      const element = document.createElement('a');
      const file = new Blob([JSON.stringify(messages, null, 2)], {type: 'text/plain'});
      element.href = URL.createObjectURL(file);
      element.download = `harv-conversation-${module?.title || 'module'}-${new Date().toISOString().split('T')[0]}.txt`;
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
      
    } catch (error) {
      console.error('Error exporting conversation:', error);
    }
  };

  if (!module) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="spinner mb-4"></div>
          <p className="text-gray-600">Loading module...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto h-screen flex flex-col">
      {/* Header */}
      <div className="bg-primary-green text-white px-6 py-4 flex items-center justify-between shadow-lg">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/dashboard')}
            className="flex items-center gap-2 px-4 py-2 bg-white/20 rounded-lg hover:bg-white/30 transition-colors"
          >
            <ArrowLeft size={18} />
            <span className="hidden sm:inline">Back to Dashboard</span>
          </button>
          
          <div>
            <h1 className="text-xl font-semibold">{module.title}</h1>
            <p className="text-white/80 text-sm">Socratic Learning with Harv</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {connected && (
            <div className="flex items-center gap-2 text-sm bg-white/20 px-3 py-2 rounded-lg">
              <div className="w-2 h-2 bg-green-300 rounded-full"></div>
              <span className="hidden sm:inline">Connected</span>
            </div>
          )}
          
          {memoryStats && (
            <div className="flex items-center gap-2 text-sm bg-white/20 px-3 py-2 rounded-lg">
              <Brain size={16} />
              <span className="hidden sm:inline">Memory Active</span>
            </div>
          )}
          
          <button
            onClick={exportConversation}
            className="flex items-center gap-2 px-3 py-2 bg-white/20 rounded-lg hover:bg-white/30 transition-colors"
          >
            <Download size={16} />
            <span className="hidden sm:inline">Export</span>
          </button>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Main Chat */}
        <div className="flex-1 flex flex-col">
          {/* Messages */}
          <div className="flex-1 p-6 overflow-y-auto chat-scroll bg-gray-50">
            <div className="max-w-4xl mx-auto space-y-6">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {message.role === 'assistant' && (
                    <div className="w-8 h-8 bg-primary-green rounded-full flex items-center justify-center flex-shrink-0">
                      <Bot size={16} className="text-white" />
                    </div>
                  )}
                  
                  <div
                    className={`max-w-[75%] px-4 py-3 rounded-2xl ${
                      message.role === 'user'
                        ? 'bg-primary-green text-white rounded-br-sm'
                        : 'bg-white text-gray-800 rounded-bl-sm border border-gray-200 shadow-sm'
                    }`}
                  >
                    <p className="whitespace-pre-wrap leading-relaxed">
                      {message.content}
                    </p>
                    <div className={`text-xs mt-2 ${
                      message.role === 'user' ? 'text-white/70' : 'text-gray-500'
                    }`}>
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </div>
                  </div>

                  {message.role === 'user' && (
                    <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center flex-shrink-0">
                      <User size={16} className="text-gray-600" />
                    </div>
                  )}
                </div>
              ))}
              
              {loading && (
                <div className="flex gap-3 justify-start">
                  <div className="w-8 h-8 bg-primary-green rounded-full flex items-center justify-center flex-shrink-0">
                    <Bot size={16} className="text-white" />
                  </div>
                  <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm">
                    <div className="flex items-center gap-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Input Area */}
          <div className="border-t border-gray-200 bg-white p-4">
            <div className="max-w-4xl mx-auto flex gap-3">
              <textarea
                ref={inputRef}
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me anything about this module, share your thoughts, or explore a concept..."
                className="flex-1 resize-none border border-gray-300 rounded-xl px-4 py-3 focus:ring-2 focus:ring-primary-green focus:border-transparent transition-colors"
                rows="2"
                disabled={loading}
              />
              <button
                onClick={sendMessage}
                disabled={loading || !inputMessage.trim()}
                className="px-6 py-3 bg-primary-green text-white rounded-xl hover:bg-primary-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 font-medium"
              >
                <Send size={18} />
                <span className="hidden sm:inline">Send</span>
              </button>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="w-80 bg-white border-l border-gray-200 p-6 overflow-y-auto">
          <div className="space-y-6">
            <div>
              <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <BookOpen size={18} />
                Module Overview
              </h3>
              <p className="text-sm text-gray-600 leading-relaxed">
                {module.description || 'Explore mass communication concepts through Socratic questioning and guided discovery.'}
              </p>
            </div>

            <div>
              <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <MessageCircle size={18} />
                Conversation Stats
              </h3>
              <div className="text-sm text-gray-600 space-y-2">
                <div className="flex justify-between">
                  <span>Messages:</span>
                  <span className="font-medium">{messages.length}</span>
                </div>
                <div className="flex justify-between">
                  <span>Status:</span>
                  <span className={`font-medium ${connected ? 'text-green-600' : 'text-red-600'}`}>
                    {connected ? 'Connected' : 'Disconnected'}
                  </span>
                </div>
                {conversationId && (
                  <div className="flex justify-between">
                    <span>Session:</span>
                    <span className="font-medium text-xs">{conversationId.slice(0, 8)}...</span>
                  </div>
                )}
              </div>
            </div>

            {memoryStats && (
              <div>
                <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <Brain size={18} />
                  Learning Context
                </h3>
                <div className="text-sm text-gray-600 space-y-2">
                  <p>✅ Memory system active</p>
                  <p>📊 Context: {memoryStats.context_length || '0'} chars</p>
                  <p>💬 Sessions: {memoryStats.conversation_count || '0'}</p>
                </div>
              </div>
            )}

            <div>
              <h3 className="font-semibold text-gray-900 mb-3">Socratic Method</h3>
              <div className="text-sm text-gray-600 space-y-2">
                <p>• Questions guide discovery</p>
                <p>• No direct answers given</p>
                <p>• Think out loud</p>
                <p>• Build on insights</p>
                <p>• Export for review</p>
              </div>
            </div>

            <div className="bg-beige-soft p-4 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-2">💡 Pro Tip</h4>
              <p className="text-sm text-gray-700">
                The more you share your thinking process, the better Harv can guide your learning journey!
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ModulePage;
