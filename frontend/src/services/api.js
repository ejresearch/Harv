const API_BASE = process.env.NODE_ENV === 'production' 
  ? 'https://your-backend.railway.app'  // Your Railway backend URL
  : 'http://127.0.0.1:8000';

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

    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // Auth endpoints
  async register(userData) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async login(credentials) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
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

  // Chat endpoints
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

  async exportConversation(data) {
    return this.request('/export', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
}

export default new ApiService();
