import React, { useState, useEffect } from 'react';
import { ArrowLeft, ChevronDown, Sun, Moon, Mail, MessageCircle } from 'lucide-react';

const FAQPage = () => {
  const [darkMode, setDarkMode] = useState(false);
  const [openFAQ, setOpenFAQ] = useState(null);

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

  // Comprehensive FAQ content per specifications
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
      question: "How do I export my chat logs?",
      answer: "In any module chat interface, click the 'Export PDF' or 'Export TXT' buttons in the top right corner. This downloads your conversation for submission to your instructor or for your personal records."
    },
    {
      question: "Can I have multiple conversations per module?",
      answer: "Yes! Each module supports multiple distinct conversations. Click 'New Conversation' in the module interface to start fresh discussions on different aspects of the module content."
    },
    {
      question: "Where can I find module resources?",
      answer: "Module-specific resources like lecture slides, readings, and supplementary materials are available in the left sidebar when you open any module. Click on any resource to access it."
    },
    {
      question: "What should I do if Harv isn't responding?",
      answer: "First, check your internet connection and refresh the page. If the problem persists, try starting a new conversation. For ongoing technical issues, contact your instructor or technical support."
    },
    {
      question: "How long should I spend on each module?",
      answer: "Most students spend 45-90 minutes per module, but focus on the quality of your engagement rather than time spent. Continue the dialogue until you feel confident in your understanding of the key concepts."
    },
    {
      question: "Can I access this platform on mobile devices?",
      answer: "Yes! The Primer Initiative platform is fully responsive and works on all devices. However, for longer conversations and accessing resources, a desktop or tablet experience is recommended."
    },
    {
      question: "Is my conversation data secure and private?",
      answer: "Absolutely. Your conversations are encrypted and only accessible to you and your instructor. We follow strict privacy guidelines and never share your data with third parties."
    },
    {
      question: "What if I forget my password?",
      answer: "Contact your instructor or course administrator for password reset assistance. They can help you regain access to your account and conversation history."
    },
    {
      question: "How do I know if I've completed a module?",
      answer: "Module completion is tracked automatically based on your engagement. Your dashboard will show completed modules with a green indicator. Your instructor may also provide specific completion criteria."
    },
    {
      question: "Can I go back to previous conversations?",
      answer: "Yes! All your conversations are saved and accessible from the conversation list in each module. You can continue any previous discussion at any time."
    }
  ];

  const handleBack = () => {
    alert('Would navigate back to Dashboard');
  };

  const handleContactInstructor = () => {
    alert('Would open instructor contact form or email');
  };

  const handleTechnicalSupport = () => {
    alert('Would open technical support contact');
  };

  // Updated color palette
  const themeClasses = {
    bg: darkMode ? 'bg-gray-900' : 'bg-[#D6CDB8]',
    cardBg: darkMode ? 'bg-gray-800' : 'bg-white',
    text: darkMode ? 'text-white' : 'text-[#222222]',
    textMuted: darkMode ? 'text-gray-400' : 'text-[#222222]',
    textSubtle: darkMode ? 'text-gray-500' : 'text-gray-600',
    border: darkMode ? 'border-gray-700' : 'border-gray-200',
    hover: darkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-50',
    hoverText: darkMode ? 'hover:text-gray-200' : 'hover:text-[#222222]',
    button: darkMode 
      ? 'bg-white text-gray-900 hover:bg-gray-100' 
      : 'bg-[#3E5641] text-white hover:bg-[#2D3F2F]'
  };

  return (
    <div className={`min-h-screen ${themeClasses.bg}`} style={{ fontFamily: 'Nunito, sans-serif' }}>
      {/* Header */}
      <div className={`${themeClasses.cardBg} border-b ${themeClasses.border} px-8 py-6 shadow-sm`}>
        <div className="flex items-center justify-between">
          <button
            onClick={handleBack}
            className={`${themeClasses.textSubtle} ${themeClasses.hoverText} flex items-center gap-2 text-base transition-colors`}
          >
            <ArrowLeft size={20} />
            Back to Dashboard
          </button>

          <button
            onClick={toggleTheme}
            className={`p-2 rounded-lg ${themeClasses.textMuted} ${themeClasses.hoverText} transition-colors`}
          >
            {darkMode ? <Sun size={20} /> : <Moon size={20} />}
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-8 py-12">
        <div className="mb-12">
          <h1 className={`text-3xl font-semibold ${themeClasses.text} mb-3`}>Help & FAQ</h1>
          <p className={`text-lg ${themeClasses.textMuted}`}>
            Common questions about using the Primer Initiative platform
          </p>
        </div>

        {/* Accordion-style FAQ List */}
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
                  className={`${themeClasses.textSubtle} transition-transform flex-shrink-0 ${
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

        {/* Contact Section */}
        <div className={`${themeClasses.cardBg} rounded-xl p-8 shadow-sm border ${themeClasses.border}`}>
          <h2 className={`text-xl font-semibold ${themeClasses.text} mb-3`}>
            Still need help?
          </h2>
          <p className={`text-base ${themeClasses.textMuted} mb-6 leading-relaxed`}>
            If you can't find the answer you're looking for, our support team is here to help. 
            Contact your instructor for course-related questions or technical support for platform issues.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4">
            <button
              onClick={handleContactInstructor}
              className={`flex items-center gap-3 px-6 py-4 rounded-xl ${themeClasses.button} transition-colors shadow-sm font-semibold`}
            >
              <Mail size={20} />
              Contact Instructor
            </button>
            
            <button
              onClick={handleTechnicalSupport}
              className={`flex items-center gap-3 px-6 py-4 rounded-xl border-2 ${themeClasses.border} ${themeClasses.hover} transition-colors font-semibold ${themeClasses.text}`}
            >
              <MessageCircle size={20} />
              Technical Support
            </button>
          </div>
        </div>

        {/* Platform Info */}
        <div className="mt-12 text-center">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="w-2 h-2 bg-[#3E5641] rounded-full"></div>
            <span className={`text-base ${themeClasses.textSubtle} font-medium`}>
              Powered by AI • Socratic Method • Always Learning
            </span>
            <div className="w-2 h-2 bg-[#3E5641] rounded-full"></div>
          </div>
          
          <div className={`text-lg font-bold ${themeClasses.text}`} style={{ fontFamily: 'Nunito, sans-serif' }}>
            <span className="relative">
              h
              <span className="absolute -top-1 -right-1 text-[#3E5641] text-sm">🌿</span>
              arv
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FAQPage;
