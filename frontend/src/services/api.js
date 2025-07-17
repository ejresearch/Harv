// Complete Harv API Service - Matches your FastAPI backend exactly
const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

class ApiService {
  constructor() {
    this.baseURL = API_BASE;
    this.token = localStorage.getItem('token');
  }

  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('token', token);
    } else {
      localStorage.removeItem('token');
    }
  }

  async request(endpoint, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...(this.token && { Authorization: `Bearer ${this.token}` }),
      ...options.headers,
    };

    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        ...options,
        headers,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // Authentication endpoints
  async register(userData) {
    const response = await this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
    
    if (response.access_token) {
      this.setToken(response.access_token);
    }
    
    return response;
  }

  async login(credentials) {
    const response = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
    
    if (response.access_token) {
      this.setToken(response.access_token);
    }
    
    return response;
  }

  logout() {
    this.setToken(null);
    localStorage.removeItem('user');
  }

  // Module endpoints
  async getModules() {
    return this.request('/modules');
  }

  async getModuleConfig(id) {
    return this.request(`/modules/${id}/config`);
  }

  // Chat endpoints - Your Socratic engine
  async sendMessage(data) {
    return this.request('/chat/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getConversationHistory(data) {
    return this.request('/conversation/history', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Memory system
  async getMemoryStats(moduleId) {
    return this.request(`/memory/stats/${moduleId}`);
  }

  async saveMemorySummary(data) {
    return this.request('/memory/summary', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Export functionality
  async exportConversation(data) {
    return this.request('/export', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Health check
  async healthCheck() {
    return this.request('/health');
  }
}

export default new ApiService();
