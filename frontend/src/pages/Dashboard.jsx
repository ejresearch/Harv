import React, { useState, useEffect } from 'react';
import { LogOut, User, Sun, Moon, HelpCircle } from 'lucide-react';

// 15 Mass Communication modules per specifications
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

const Dashboard = () => {
  const [darkMode, setDarkMode] = useState(false);
  const [user] = useState({ name: "Alex Johnson", email: "alex.johnson@university.edu" });
  const [completedModules] = useState(new Set([0, 1, 2])); // Mock completed modules

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

  const handleModuleSelect = (moduleTitle, index) => {
    alert(`Opening Module ${index + 1}: ${moduleTitle}\n\nNext: Module chat interface would load!`);
  };

  const handleFAQ = () => {
    alert('FAQ/Help page would open!');
  };

  const handleExitSurvey = () => {
    alert('Exit Survey would open!');
  };

  const handleLogout = () => {
    alert('Logged out! Would return to Landing Page.');
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
    moduleCard: darkMode ? 'bg-gray-800 hover:bg-gray-700' : 'bg-white hover:bg-gray-50'
  };

  return (
    <div className={`min-h-screen ${themeClasses.bg}`} style={{ fontFamily: 'Nunito, sans-serif' }}>
      {/* Header */}
      <div className={`${themeClasses.cardBg} border-b ${themeClasses.border} shadow-sm`}>
        <div className="max-w-6xl mx-auto px-8 py-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            {/* Logo */}
            <div className={`text-2xl font-bold ${themeClasses.text}`} style={{ fontFamily: 'Nunito, sans-serif' }}>
              <span className="relative">
                h
                <span className="absolute -top-1 -right-1 text-[#3E5641] text-sm">🌿</span>
                arv
              </span>
            </div>
            <span className={`font-semibold text-xl ${themeClasses.text}`}>Primer Initiative</span>
          </div>

          <div className="flex items-center gap-6">
            <button
              onClick={toggleTheme}
              className={`p-2 rounded-lg ${themeClasses.textMuted} ${themeClasses.hoverText} transition-colors`}
            >
              {darkMode ? <Sun size={20} /> : <Moon size={20} />}
            </button>

            <div className={`flex items-center gap-3 text-base ${themeClasses.textMuted}`}>
              <User size={18} />
              {user.name}
            </div>
            
            <button
              onClick={handleLogout}
              className={`text-base ${themeClasses.textSubtle} ${themeClasses.hoverText} flex items-center gap-2 transition-colors`}
            >
              <LogOut size={18} />
              Sign out
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-8 py-12">
        {/* Personalized Greeting */}
        <div className="mb-12">
          <h1 className={`text-3xl font-semibold ${themeClasses.text} mb-3`}>
            Welcome, {user.name.split(' ')[0]}
          </h1>
          <p className={`text-lg ${themeClasses.textMuted}`}>
            Continue your mass communication learning journey
          </p>
        </div>

        {/* Progress Overview */}
        <div className="mb-12 flex items-center gap-8">
          <div className="flex items-center gap-3">
            <div className="w-4 h-4 bg-[#3E5641] rounded-full"></div>
            <span className={`text-lg ${themeClasses.textMuted} font-medium`}>
              {completedModules.size} of {modules.length} modules completed
            </span>
          </div>
          <div className={`text-base ${themeClasses.textSubtle}`}>
            {Math.round((completedModules.size / modules.length) * 100)}% Progress
          </div>
        </div>

        {/* Linear List of 15 Modules */}
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
                        <span className={`text-lg ${themeClasses.textSubtle} font-bold font-mono w-12`}>
                          {String(index + 1).padStart(2, '0')}
                        </span>
                        {isCompleted && (
                          <div className="w-3 h-3 bg-[#3E5641] rounded-full"></div>
                        )}
                      </div>
                      <div>
                        <h3 className={`text-lg font-semibold ${themeClasses.text} ${themeClasses.hoverText} transition-colors ${isCompleted ? 'opacity-75' : ''}`}>
                          {title}
                        </h3>
                        <p className={`text-base ${themeClasses.textSubtle} mt-1`}>
                          {isCompleted ? 'Completed' : 'Ready to start'}
                        </p>
                      </div>
                    </div>
                    <div className={`${themeClasses.textSubtle} group-hover:${themeClasses.textMuted} transition-colors`}>
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

        {/* Navigation to FAQ/Help and Exit Survey */}
        <div className="flex gap-6">
          <button
            onClick={handleFAQ}
            className={`flex items-center gap-3 px-6 py-4 rounded-xl ${themeClasses.moduleCard} transition-colors border ${themeClasses.border} shadow-sm`}
          >
            <HelpCircle size={20} className="text-[#3E5641]" />
            <span className={`text-lg font-medium ${themeClasses.text}`}>FAQ & Help</span>
          </button>
          
          <button
            onClick={handleExitSurvey}
            className={`flex items-center gap-3 px-6 py-4 rounded-xl ${themeClasses.moduleCard} transition-colors border ${themeClasses.border} shadow-sm`}
          >
            <div className="w-5 h-5 bg-[#3E5641] rounded-full flex items-center justify-center">
              <span className="text-white text-xs">✓</span>
            </div>
            <span className={`text-lg font-medium ${themeClasses.text}`}>Exit Survey</span>
          </button>
        </div>

        {/* Footer */}
        <div className={`mt-16 pt-8 border-t ${themeClasses.border} text-center`}>
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="w-2 h-2 bg-[#3E5641] rounded-full"></div>
            <span className={`text-base ${themeClasses.textSubtle} font-medium`}>
              Powered by AI • Socratic Method • Personalized Learning
            </span>
            <div className="w-2 h-2 bg-[#3E5641] rounded-full"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
