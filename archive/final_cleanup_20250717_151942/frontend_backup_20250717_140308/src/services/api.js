// Harv Platform API Service
// Connects to your backend running on port 8000
import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
});

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token');
      window.location.href = '/'; // Redirect to landing
    }
    return Promise.reject(error);
  }
);

// Authentication endpoints (matches your backend exactly)
export const auth = {
  // Register new user with onboarding data
  register: async (email, password, onboardingData = {}) => {
    try {
      const response = await api.post('/auth/register', {
        email,
        password,
        ...onboardingData
      });
      
      // Your backend returns 'access_token' (not 'accessToken')
      if (response.data.access_token) {
        localStorage.setItem('access_token', response.data.access_token);
      }
      
      return response.data;
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  },

  // Login existing user
  login: async (email, password) => {
    try {
      const response = await api.post('/auth/login', {
        email,
        password
      });
      
      // Your backend returns 'access_token' (standardized format)
      if (response.data.access_token) {
        localStorage.setItem('access_token', response.data.access_token);
      }
      
      return response.data;
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  },

  // Logout user
  logout: () => {
    localStorage.removeItem('access_token');
    window.location.href = '/';
  },

  // Get current user info
  getCurrentUser: async () => {
    try {
      const response = await api.get('/auth/me');
      return response.data;
    } catch (error) {
      console.error('Failed to get current user:', error);
      throw error;
    }
  }
};

// Module endpoints (matches your working backend)
export const modules = {
  // Get all 15 modules from your database
  getAll: async () => {
    try {
      const response = await api.get('/modules');
      return response.data; // Your backend returns array of modules
    } catch (error) {
      console.error('Failed to load modules:', error);
      throw error;
    }
  },

  // Get specific module details
  getById: async (moduleId) => {
    try {
      const response = await api.get(`/modules/${moduleId}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to load module ${moduleId}:`, error);
      throw error;
    }
  },

  // Get module configuration (Socratic prompts, etc.)
  getConfig: async (moduleId) => {
    try {
      const response = await api.get(`/modules/${moduleId}/config`);
      return response.data;
    } catch (error) {
      console.error(`Failed to load config for module ${moduleId}:`, error);
      throw error;
    }
  },

  // Get module resources (slides, readings, etc.)
  getResources: async (moduleId) => {
    try {
      const response = await api.get(`/modules/${moduleId}/resources`);
      return response.data;
    } catch (error) {
      console.error(`Failed to load resources for module ${moduleId}:`, error);
      // Return empty array if resources endpoint doesn't exist yet
      return [];
    }
  }
};

// Chat endpoints (matches your Socratic AI system)
export const chat = {
  // Send message to Harv AI (your Socratic engine)
  sendMessage: async (moduleId, message, conversationId = null) => {
    try {
      const response = await api.post('/chat/', {
        module_id: moduleId,
        message: message,
        conversation_id: conversationId
      });
      
      // Your backend returns 'reply' field (standardized format)
      return {
        reply: response.data.reply,
        conversation_id: response.data.conversation_id,
        message_id: response.data.message_id
      };
    } catch (error) {
      console.error('Failed to send message:', error);
      throw error;
    }
  },

  // Get conversation history
  getHistory: async (conversationId) => {
    try {
      const response = await api.get(`/chat/history/${conversationId}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to load conversation ${conversationId}:`, error);
      throw error;
    }
  },

  // Get all conversations for a module
  getConversations: async (moduleId) => {
    try {
      const response = await api.get(`/chat/conversations/${moduleId}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to load conversations for module ${moduleId}:`, error);
      return [];
    }
  },

  // Start new conversation
  startConversation: async (moduleId, title = 'New Conversation') => {
    try {
      const response = await api.post('/chat/start', {
        module_id: moduleId,
        title: title
      });
      return response.data;
    } catch (error) {
      console.error('Failed to start conversation:', error);
      throw error;
    }
  },

  // Export conversation as PDF
  exportPDF: async (conversationId) => {
    try {
      const response = await api.get(`/chat/export/${conversationId}/pdf`, {
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `conversation_${conversationId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      return true;
    } catch (error) {
      console.error('Failed to export PDF:', error);
      throw error;
    }
  },

  // Export conversation as TXT
  exportTXT: async (conversationId) => {
    try {
      const response = await api.get(`/chat/export/${conversationId}/txt`, {
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `conversation_${conversationId}.txt`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      return true;
    } catch (error) {
      console.error('Failed to export TXT:', error);
      throw error;
    }
  }
};

// Health check endpoint
export const health = {
  check: async () => {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }
};

// Memory system endpoints (for your multi-layer memory)
export const memory = {
  // Get memory stats for a module
  getStats: async (moduleId) => {
    try {
      const response = await api.get(`/memory/stats/${moduleId}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to load memory stats for module ${moduleId}:`, error);
      throw error;
    }
  },

  // Get assembled context (your 1700+ character memory system)
  getContext: async (moduleId, conversationId = null) => {
    try {
      const response = await api.get(`/memory/context/${moduleId}`, {
        params: { conversation_id: conversationId }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to load memory context:', error);
      throw error;
    }
  }
};

// Utility functions
export const utils = {
  // Check if backend is available
  isBackendAvailable: async () => {
    try {
      await health.check();
      return true;
    } catch (error) {
      return false;
    }
  },

  // Format error messages for user display
  formatError: (error) => {
    if (error.response?.data?.detail) {
      return error.response.data.detail;
    }
    if (error.response?.data?.message) {
      return error.response.data.message;
    }
    if (error.message) {
      return error.message;
    }
    return 'An unexpected error occurred';
  },

  // Check if user is authenticated
  isAuthenticated: () => {
    return !!localStorage.getItem('access_token');
  }
};

// Default export with all services
export default {
  auth,
  modules,
  chat,
  health,
  memory,
  utils
};
