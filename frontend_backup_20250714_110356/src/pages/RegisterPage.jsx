import React, { useState, useEffect } from 'react';
import { ArrowLeft, Loader2, Sun, Moon } from 'lucide-react';

const RegisterPage = () => {
  const [darkMode, setDarkMode] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  
  // Onboarding survey fields (directly embedded)
  const [reason, setReason] = useState('');
  const [familiarity, setFamiliarity] = useState('');
  const [learningStyle, setLearningStyle] = useState('');
  const [goals, setGoals] = useState('');
  const [background, setBackground] = useState('');
  
  const [loading, setLoading] = useState(false);

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

  const handleSubmit = () => {
    if (email && password && name && reason && familiarity && learningStyle) {
      setLoading(true);
      setTimeout(() => {
        setLoading(false);
        alert(`Registration successful!\n\nNext: Dashboard would load with 15 modules!`);
      }, 2000);
    } else {
      alert('Please fill in all required fields');
    }
  };

  const handleBack = () => {
    alert('Would navigate back to Landing Page');
  };

  // Updated color palette
  const themeClasses = {
    bg: darkMode ? 'bg-gray-900' : 'bg-[#D6CDB8]',
    cardBg: darkMode ? 'bg-gray-800' : 'bg-white',
    text: darkMode ? 'text-white' : 'text-[#222222]',
    textMuted: darkMode ? 'text-gray-400' : 'text-[#222222]',
    textSubtle: darkMode ? 'text-gray-500' : 'text-gray-600',
    input: darkMode 
      ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400 focus:ring-[#3E5641] focus:border-[#3E5641]' 
      : 'bg-white border-gray-300 text-[#222222] placeholder-gray-500 focus:ring-[#3E5641] focus:border-[#3E5641]',
    button: darkMode 
      ? 'bg-white text-gray-900 hover:bg-gray-100' 
      : 'bg-[#3E5641] text-white hover:bg-[#2D3F2F]'
  };

  const completionSteps = [
    email && password && name,
    reason && familiarity,
    learningStyle && goals
  ];

  return (
    <div className={`min-h-screen ${themeClasses.bg} flex items-center justify-center px-6 py-8`} style={{ fontFamily: 'Nunito, sans-serif' }}>
      {/* Theme Toggle */}
      <button
        onClick={toggleTheme}
        className={`fixed top-6 right-6 p-3 rounded-lg ${darkMode ? 'text-gray-400 hover:text-gray-200' : 'text-[#3E5641] hover:text-[#222222]'} transition-colors`}
      >
        {darkMode ? <Sun size={24} /> : <Moon size={24} />}
      </button>

      <div className="w-full max-w-md">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={handleBack}
            className={`${themeClasses.textSubtle} hover:${themeClasses.text} mb-8 flex items-center gap-2 text-base transition-colors`}
          >
            <ArrowLeft size={20} />
            Back
          </button>
          
          {/* Logo */}
          <div className="text-center mb-8">
            <div className={`text-3xl font-bold ${themeClasses.text} mb-2`} style={{ fontFamily: 'Nunito, sans-serif' }}>
              <span className="relative">
                h
                <span className="absolute -top-1 -right-1 text-[#3E5641] text-lg">🌿</span>
                arv
              </span>
            </div>
          </div>
          
          <h1 className={`text-2xl font-semibold ${themeClasses.text} text-center mb-2`}>Create Your Account</h1>
          <p className={`text-base ${themeClasses.textMuted} text-center`}>Join the Primer Initiative learning experience</p>
        </div>

        {/* Single-page registration with embedded onboarding */}
        <div className={`${themeClasses.cardBg} rounded-xl p-8 shadow-lg`}>
          <div className="space-y-6">
            {/* Basic Registration Fields */}
            <div className="space-y-4">
              <h3 className={`text-lg font-semibold ${themeClasses.text} mb-4`}>Account Information</h3>
              
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Full Name"
                className={`w-full px-4 py-4 border rounded-lg text-base focus:outline-none focus:ring-2 ${themeClasses.input}`}
                required
              />

              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Email Address"
                className={`w-full px-4 py-4 border rounded-lg text-base focus:outline-none focus:ring-2 ${themeClasses.input}`}
                required
              />

              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Password"
                className={`w-full px-4 py-4 border rounded-lg text-base focus:outline-none focus:ring-2 ${themeClasses.input}`}
                required
              />
            </div>

            {/* Embedded Onboarding Survey */}
            <div className="space-y-4 pt-6 border-t border-gray-200 dark:border-gray-600">
              <h3 className={`text-lg font-semibold ${themeClasses.text} mb-4`}>Learning Profile</h3>
              
              <textarea
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder="Why are you taking this mass communication course?"
                className={`w-full px-4 py-4 border rounded-lg text-base focus:outline-none focus:ring-2 resize-none ${themeClasses.input}`}
                rows="3"
                required
              />

              <select
                value={familiarity}
                onChange={(e) => setFamiliarity(e.target.value)}
                className={`w-full px-4 py-4 border rounded-lg text-base focus:outline-none focus:ring-2 ${themeClasses.input}`}
                required
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
                required
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

              <input
                type="text"
                value={background}
                onChange={(e) => setBackground(e.target.value)}
                placeholder="Academic or professional background (optional)"
                className={`w-full px-4 py-4 border rounded-lg text-base focus:outline-none focus:ring-2 ${themeClasses.input}`}
              />
            </div>

            <button
              onClick={handleSubmit}
              disabled={loading}
              className={`w-full py-4 rounded-lg text-lg font-semibold transition-colors disabled:opacity-50 flex items-center justify-center shadow-sm ${themeClasses.button}`}
            >
              {loading ? <Loader2 className="animate-spin mr-2" size={20} /> : null}
              {loading ? 'Creating Account...' : 'Create Account'}
            </button>
          </div>

          {/* Progress indicator */}
          <div className="mt-8 flex justify-center">
            <div className="flex gap-2">
              {completionSteps.map((completed, index) => (
                <div
                  key={index}
                  className={`w-3 h-3 rounded-full transition-colors ${
                    completed ? 'bg-[#3E5641]' : darkMode ? 'bg-gray-600' : 'bg-gray-300'
                  }`}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
