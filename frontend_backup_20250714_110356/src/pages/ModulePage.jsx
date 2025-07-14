import React, { useState, useEffect } from 'react';
import { ArrowLeft, Send, Download, FileText, Loader2, Sun, Moon, Plus, MessageSquare, BookOpen, Monitor } from 'lucide-react';

const ModulePage = () => {
  const [darkMode, setDarkMode] = useState(false);
  const [currentConversationId, setCurrentConversationId] = useState(1);
  const [conversations, setConversations] = useState({
    1: {
      id: 1,
      title: "Understanding Media Influence",
      messages: [
        {
          role: 'assistant',
          content: 'Hello! I\'m Harv, your Socratic tutor for Module 1: Introduction to Mass Communication. Instead of giving you direct answers, I\'ll guide you to discover insights through thoughtful questions.\n\nWhat aspects of mass media\'s influence on daily life do you find most intriguing?'
        }
      ],
      lastActivity: new Date().toISOString()
    },
    2: {
      id: 2,
      title: "Media Theory Discussion",
      messages: [
        {
          role: 'assistant',
          content: 'Welcome back! Let\'s explore media theory together. What questions do you have about how different media formats affect message reception?'
        },
        {
          role: 'user',
          content: 'I\'ve been thinking about how social media changes the way we consume news compared to traditional newspapers.'
        },
        {
          role: 'assistant',
          content: 'That\'s a fascinating observation! What specific differences have you noticed in how you personally engage with news on social media versus when reading a physical newspaper? Consider your attention span, the depth of articles you read, and how you verify information.'
        }
      ],
      lastActivity: new Date(Date.now() - 86400000).toISOString()
    }
  });
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [showResources, setShowResources] = useState(true);

  const module = {
    id: 1,
    title: "Introduction to Mass Communication",
    resources: [
      { title: "Lecture Slides: Media Fundamentals", type: "slides", url: "#" },
      { title: "Reading: Communication Theory Basics", type: "reading", url: "#" },
      { title: "Case Study: Social Media Impact", type: "reading", url: "#" },
      { title: "Video: History of Mass Media", type: "video", url: "#" }
    ]
  };

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

  const socraticResponses = [
    "That's an insightful observation! What evidence have you seen that supports this perspective? Can you think of a specific example?",
    "Excellent question! Before we explore that together, what's your initial thinking? What patterns have you noticed?",
    "You're making important connections. How might this principle apply differently across various demographic groups or cultures?",
    "That's a thoughtful response. What questions does this raise for you about the responsibility of media creators and consumers?",
    "I can see you're thinking deeply about this. If you were to challenge that assumption, what counterarguments might emerge?",
    "Very perceptive! How do you think this concept has evolved with the rise of digital and social media platforms?",
    "Interesting perspective! What led you to that conclusion? Can you walk me through your reasoning?"
  ];

  const currentConversation = conversations[currentConversationId];

  const sendMessage = () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    const updatedConversations = {
      ...conversations,
      [currentConversationId]: {
        ...currentConversation,
        messages: [...currentConversation.messages, userMessage],
        lastActivity: new Date().toISOString()
      }
    };
    setConversations(updatedConversations);
    setInput('');
    setLoading(true);

    setTimeout(() => {
      const randomResponse = socraticResponses[Math.floor(Math.random() * socraticResponses.length)];
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

  const exportChatPDF = () => {
    alert('PDF export functionality would generate a formatted PDF of the conversation');
  };

  const exportChatTXT = () => {
    const chatText = currentConversation.messages.map(msg =>
      `${msg.role === 'user' ? 'Student' : 'Harv'}: ${msg.content}`
    ).join('\n\n');

    const blob = new Blob([chatText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `module-${module.id}-${currentConversation.title.replace(/\s+/g, '-')}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleBack = () => {
    alert('Would navigate back to Dashboard');
  };

  const formatTime = (isoString) => {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffHours < 1) return 'Just now';
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  const getResourceIcon = (type) => {
    switch (type) {
      case 'slides': return <Monitor size={16} className="text-[#3E5641]" />;
      case 'reading': return <BookOpen size={16} className="text-[#3E5641]" />;
      case 'video': return <FileText size={16} className="text-[#3E5641]" />;
      default: return <FileText size={16} className="text-[#3E5641]" />;
    }
  };

  // Updated color palette
  const themeClasses = {
    bg: darkMode ? 'bg-gray-900' : 'bg-[#D6CDB8]',
    cardBg: darkMode ? 'bg-gray-800' : 'bg-white',
    sidebarBg: darkMode ? 'bg-gray-800' : 'bg-white',
    text: darkMode ? 'text-white' : 'text-[#222222]',
    textMuted: darkMode ? 'text-gray-400' : 'text-[#222222]',
    textSubtle: darkMode ? 'text-gray-500' : 'text-gray-600',
    border: darkMode ? 'border-gray-700' : 'border-gray-200',
    input: darkMode 
      ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400 focus:ring-[#3E5641] focus:border-[#3E5641]' 
      : 'bg-white border-gray-300 text-[#222222] placeholder-gray-500 focus:ring-[#3E5641] focus:border-[#3E5641]',
    button: darkMode 
      ? 'bg-white text-gray-900 hover:bg-gray-100' 
      : 'bg-[#3E5641] text-white hover:bg-[#2D3F2F]',
    avatar: darkMode ? 'bg-gray-700 text-gray-300' : 'bg-gray-100 text-[#222222]',
    hover: darkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-50',
    hoverText: darkMode ? 'hover:text-gray-200' : 'hover:text-[#222222]',
    active: darkMode ? 'bg-gray-700 border-gray-600' : 'bg-[#3E5641] bg-opacity-10 border-[#3E5641]'
  };

  return (
    <div className={`min-h-screen ${themeClasses.bg} flex`} style={{ fontFamily: 'Nunito, sans-serif' }}>
      {/* Resources Sidebar */}
      {showResources && (
        <div className={`w-80 ${themeClasses.sidebarBg} border-r ${themeClasses.border} flex flex-col shadow-lg`}>
          {/* Sidebar Header */}
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <h2 className={`font-semibold ${themeClasses.text} text-lg`}>
                Module Resources
              </h2>
              <button
                onClick={toggleTheme}
                className={`p-2 rounded-lg ${themeClasses.textMuted} ${themeClasses.hoverText} transition-colors`}
              >
                {darkMode ? <Sun size={18} /> : <Moon size={18} />}
              </button>
            </div>
            <button
              onClick={createNewConversation}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl ${themeClasses.border} border ${themeClasses.hover} transition-colors text-base ${themeClasses.textMuted} font-medium`}
            >
              <Plus size={18} />
              New Conversation
            </button>
          </div>

          {/* Module Resources */}
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
                    {getResourceIcon(resource.type)}
                    <span className={`text-sm font-medium ${themeClasses.text} ${themeClasses.hoverText} transition-colors`}>
                      {resource.title}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Conversations List */}
          <div className="flex-1 overflow-y-auto p-4">
            <h3 className={`font-semibold ${themeClasses.text} mb-4 text-base`}>Your Conversations</h3>
            {Object.values(conversations)
              .sort((a, b) => new Date(b.lastActivity) - new Date(a.lastActivity))
              .map((conversation) => (
                <button
                  key={conversation.id}
                  onClick={() => setCurrentConversationId(conversation.id)}
                  className={`w-full text-left p-4 rounded-xl mb-3 transition-colors border ${
                    conversation.id === currentConversationId
                      ? themeClasses.active
                      : `${themeClasses.hover} border-transparent`
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        <MessageSquare size={16} className={themeClasses.textMuted} />
                        <span className={`text-base font-semibold ${themeClasses.text} truncate`}>
                          {conversation.title}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className={`text-sm ${themeClasses.textSubtle}`}>
                          {conversation.messages.length} messages
                        </span>
                        <span className={`text-sm ${themeClasses.textSubtle}`}>
                          {formatTime(conversation.lastActivity)}
                        </span>
                      </div>
                    </div>
                  </div>
                </button>
              ))}
          </div>
        </div>
      )}

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className={`${themeClasses.cardBg} border-b ${themeClasses.border} px-8 py-6 shadow-sm`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              <button
                onClick={handleBack}
                className={`${themeClasses.textSubtle} ${themeClasses.hoverText} flex items-center gap-2 text-base transition-colors`}
              >
                <ArrowLeft size={20} />
                Back to Dashboard
              </button>
              <div>
                <h1 className={`font-semibold ${themeClasses.text} text-xl`}>
                  {module.title}
                </h1>
                <p className={`text-base ${themeClasses.textSubtle} mt-1`}>
                  Harv Chat: {currentConversation.title}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <button
                onClick={() => setShowResources(!showResources)}
                className={`p-3 rounded-lg ${themeClasses.textMuted} ${themeClasses.hoverText} transition-colors`}
              >
                <BookOpen size={20} />
              </button>
              
              <div className="flex items-center gap-2">
                <button
                  onClick={exportChatPDF}
                  className={`text-base ${themeClasses.textSubtle} ${themeClasses.hoverText} flex items-center gap-2 transition-colors px-4 py-2 rounded-lg ${themeClasses.hover}`}
                >
                  <FileText size={16} />
                  Export PDF
                </button>
                <button
                  onClick={exportChatTXT}
                  className={`text-base ${themeClasses.textSubtle} ${themeClasses.hoverText} flex items-center gap-2 transition-colors px-4 py-2 rounded-lg ${themeClasses.hover}`}
                >
                  <Download size={16} />
                  Export TXT
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Chat Messages */}
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
                    <div className={`flex items-center gap-3 text-base ${themeClasses.textSubtle}`}>
                      <Loader2 size={18} className="animate-spin" />
                      Harv is thinking...
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Input Area */}
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
                  style={{ minHeight: '56px', maxHeight: '120px' }}
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
              <p className={`text-sm ${themeClasses.textSubtle}`}>
                Press Enter to send, Shift+Enter for new line
              </p>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-[#3E5641] rounded-full"></div>
                <span className={`text-sm ${themeClasses.textSubtle}`}>
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

export default ModulePage;
