import React, { useState, useEffect } from 'react';
import { Sun, Moon } from 'lucide-react';

const LandingPage = () => {
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    // Check for saved theme preference or default to light mode
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      setDarkMode(savedTheme === 'dark');
    } else {
      // Check system preference
      setDarkMode(window.matchMedia('(prefers-color-scheme: dark)').matches);
    }
  }, []);

  const toggleTheme = () => {
    const newDarkMode = !darkMode;
    setDarkMode(newDarkMode);
    localStorage.setItem('theme', newDarkMode ? 'dark' : 'light');
  };

  const handleRegister = () => {
    alert('Registration page would open!');
  };

  const handleLogin = () => {
    alert('Login page would open!');
  };

  // Updated color palette per specifications
  const themeClasses = {
    bg: darkMode ? 'bg-gray-900' : 'bg-[#D6CDB8]', // Beige background
    text: darkMode ? 'text-white' : 'text-[#222222]', // Standard black
    textMuted: darkMode ? 'text-gray-400' : 'text-[#222222]',
    button: darkMode ? 'bg-white text-gray-900 hover:bg-gray-100' : 'bg-[#3E5641] text-white hover:bg-[#2D3F2F]', // Primary green
    buttonSecondary: darkMode ? 'border-gray-600 text-gray-300 hover:bg-gray-800' : 'border-[#3E5641] text-[#3E5641] hover:bg-[#3E5641] hover:text-white'
  };

  return (
    <div className={`min-h-screen ${themeClasses.bg} flex items-center justify-center px-6`} style={{ fontFamily: 'Nunito, sans-serif' }}>
      {/* Theme Toggle */}
      <button
        onClick={toggleTheme}
        className={`fixed top-6 right-6 p-3 rounded-lg ${darkMode ? 'text-gray-400 hover:text-gray-200' : 'text-[#3E5641] hover:text-[#222222]'} transition-colors`}
      >
        {darkMode ? <Sun size={24} /> : <Moon size={24} />}
      </button>

      <div className="w-full max-w-lg text-center">
        {/* Logo - Lowercase "harv" with leaf curl */}
        <div className="mb-16">
          <div className="mb-6">
            {/* Simple representation of "harv" logo with leaf curl */}
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

        {/* Action Buttons - Large and clearly labeled */}
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

        {/* Brief, inviting overview text */}
        <div className={`text-base ${themeClasses.textMuted} leading-relaxed max-w-md mx-auto`}>
          <p className="mb-4">
            Engage with 15 interactive modules designed to guide your learning through thoughtful dialogue with AI tutors.
          </p>
          <p>
            Discover insights through questions, not answers.
          </p>
        </div>

        {/* Subtle branding accent */}
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

export default LandingPage;
