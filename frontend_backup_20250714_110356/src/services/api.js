// Updated API Service - Matches standardized backend responses
const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

class ApiService {
  constructor() {
    this.baseURL = API_BASE;
  }

  async request(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    const headers = {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    };

    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        ...options,
        headers,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // Auth endpoints - Updated for standardized responses
  async register(userData) {
    const response = await this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
    
    // Backend now returns: { access_token, token_type, user_id, user: {...} }
    if (response.access_token) {
      localStorage.setItem('token', response.access_token);
      localStorage.setItem('user', JSON.stringify(response.user));
    }
    
    return response;
  }

  async login(credentials) {
    const response = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
    
    // Backend now returns: { access_token, token_type, user_id, user: {...} }
    if (response.access_token) {
      localStorage.setItem('token', response.access_token);
      localStorage.setItem('user', JSON.stringify(response.user));
    }
    
    return response;
  }

  async getProfile() {
    return this.request('/auth/me');
  }

  // Module endpoints
  async getModules() {
    return this.request('/modules');
  }

  async getModule(id) {
    return this.request(`/modules/${id}`);
  }

  // Chat endpoints - Updated for standardized responses
  async sendMessage(data) {
    const response = await this.request('/chat/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    
    // Backend now returns: { reply, conversation_id, module_id, timestamp }
    return response;
  }

  async getConversationHistory(data) {
    return this.request('/conversation/history', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async exportConversation(data) {
    return this.request('/export', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Memory endpoints
  async saveMemorySummary(data) {
    return this.request('/memory/summary', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getMemoryStats(moduleId) {
    return this.request(`/memory/stats/${moduleId}`);
  }

  // Health check
  async healthCheck() {
    return this.request('/health');
  }
}

export default new ApiService();
