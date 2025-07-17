import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { BookOpen, MessageCircle, TrendingUp, Clock, Play, ChevronRight, Brain } from 'lucide-react';
import ApiService from '../services/api';
import { useAuth } from '../context/AuthContext';

const Dashboard = () => {
  const [modules, setModules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    loadModules();
  }, []);

  const loadModules = async () => {
    try {
      setLoading(true);
      const response = await ApiService.getModules();
      setModules(Array.isArray(response) ? response : []);
    } catch (err) {
      setError('Failed to load modules. Make sure your backend is running.');
      console.error('Error loading modules:', err);
    } finally {
      setLoading(false);
    }
  };

  const startModule = (module) => {
    navigate(`/module/${module.id}`);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="spinner mb-4"></div>
          <p className="text-gray-600">Loading your modules...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      {/* Welcome Section */}
      <div className="mb-8 fade-in">
        <h1 className="text-4xl font-bold text-primary-green mb-3">
          Welcome back, {user?.name?.split(' ')[0] || user?.email?.split('@')[0]}! 👋
        </h1>
        <p className="text-xl text-gray-600">
          Ready to continue your Socratic learning journey? Choose a module below.
        </p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-primary-green/10 rounded-lg flex items-center justify-center">
              <BookOpen className="text-primary-green" size={24} />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{modules.length}</p>
              <p className="text-sm text-gray-600">Available Modules</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center">
              <MessageCircle className="text-blue-600" size={24} />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">0</p>
              <p className="text-sm text-gray-600">Conversations</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-green-50 rounded-lg flex items-center justify-center">
              <TrendingUp className="text-green-600" size={24} />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">0%</p>
              <p className="text-sm text-gray-600">Progress</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-purple-50 rounded-lg flex items-center justify-center">
              <Brain className="text-purple-600" size={24} />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">Active</p>
              <p className="text-sm text-gray-600">AI Memory</p>
            </div>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-lg mb-8">
          <p className="font-medium">Connection Error</p>
          <p className="text-sm mt-1">{error}</p>
          <button 
            onClick={loadModules}
            className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
          >
            Try again
          </button>
        </div>
      )}

      {/* Modules Section */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Communication Modules</h2>
        <p className="text-gray-600">Click any module to start learning through Socratic questioning</p>
      </div>

      {/* Modules Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {modules.map((module, index) => (
          <div
            key={module.id}
            onClick={() => startModule(module)}
            className="bg-white rounded-xl p-6 border border-gray-200 hover:border-primary-green hover:shadow-lg transition-all duration-200 cursor-pointer group fade-in"
            style={{ animationDelay: `${index * 0.1}s` }}
          >
            <div className="flex items-start justify-between mb-4">
              <div className="w-12 h-12 bg-primary-green/10 rounded-lg flex items-center justify-center group-hover:bg-primary-green group-hover:text-white transition-colors">
                <BookOpen size={24} className="group-hover:text-white text-primary-green" />
              </div>
              <div className="flex items-center text-xs bg-primary-green/10 text-primary-green px-3 py-1 rounded-full">
                Module {module.id}
              </div>
            </div>
            
            <h3 className="text-lg font-semibold text-gray-900 mb-3 group-hover:text-primary-green transition-colors">
              {module.title}
            </h3>
            
            <p className="text-gray-600 text-sm leading-relaxed mb-4 line-clamp-3">
              {module.description || 'Explore mass communication concepts through guided Socratic questioning and discovery-based learning.'}
            </p>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span>Ready to start</span>
              </div>
              <div className="flex items-center gap-1 text-primary-green group-hover:translate-x-1 transition-transform">
                <Play size={14} />
                <ChevronRight size={14} />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {modules.length === 0 && !loading && !error && (
        <div className="text-center py-16">
          <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <BookOpen className="text-gray-400" size={48} />
          </div>
          <h3 className="text-xl font-semibold text-gray-700 mb-3">No modules available</h3>
          <p className="text-gray-500 mb-6">Modules will appear here once your backend is configured.</p>
          <button 
            onClick={loadModules}
            className="bg-primary-green text-white px-6 py-2 rounded-lg hover:bg-primary-600 transition-colors"
          >
            Refresh Modules
          </button>
        </div>
      )}

      {/* Learning Tips */}
      {modules.length > 0 && (
        <div className="mt-12 bg-gradient-to-r from-primary-green/5 to-blue-50 rounded-xl p-8 border border-primary-green/20">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">💡 Socratic Learning Tips</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-700">
            <div className="flex items-start gap-3">
              <div className="w-5 h-5 bg-primary-green rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-white text-xs">1</span>
              </div>
              <p>Ask open-ended questions to explore concepts deeply</p>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-5 h-5 bg-primary-green rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-white text-xs">2</span>
              </div>
              <p>Share your thinking process - Harv learns from your reasoning</p>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-5 h-5 bg-primary-green rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-white text-xs">3</span>
              </div>
              <p>Build on previous conversations - your memory system remembers</p>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-5 h-5 bg-primary-green rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-white text-xs">4</span>
              </div>
              <p>Export conversations for study and review later</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
