// Final API Service - Matches Backend Exactly
const BASE_URL = 'http://127.0.0.1:8000';

class ApiService {
  constructor() {
    this.token = localStorage.getItem('token');
  }

  // Login: OAuth2 form data format (CONFIRMED WORKING)
  async login(credentials) {
    const formData = new URLSearchParams();
    formData.append('username', credentials.email);  // Backend expects 'username'
    formData.append('password', credentials.password);
    formData.append('grant_type', 'password');

    const response = await fetch(`${BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData
    });

    const data = await response.json();
    
    if (response.ok) {
      this.token = data.access_token;
      localStorage.setItem('token', this.token);
      return {
        success: true,
        access_token: data.access_token,
        user: data.user
      };
    } else {
      throw new Error(data.detail || 'Login failed');
    }
  }

  // Register: JSON format with REQUIRED name field + username field
  async register(userData) {
    // Backend requires: name (required), username field (for success)
    const registrationData = {
      email: userData.email,
      password: userData.password,
      name: userData.name || userData.email.split('@')[0], // REQUIRED field
      username: userData.email, // Helps with backend processing
      reason: userData.reason || 'Learning mass communication',
      familiarity: userData.familiarity || 'Beginner',
      learning_style: userData.learning_style || 'Mixed'
    };

    const response = await fetch(`${BASE_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(registrationData)
    });

    const data = await response.json();
    
    if (response.ok) {
      return {
        success: true,
        user: data.user || data,
        message: data.message || 'Registration successful'
      };
    } else {
      // Handle specific error cases
      if (response.status === 400 && data.detail?.includes('already registered')) {
        throw new Error('Email already registered. Please try logging in instead.');
      }
      throw new Error(data.detail || 'Registration failed');
    }
  }

  // Authenticated API calls
  async apiCall(endpoint, method = 'GET', data = null) {
    const headers = {
      'Authorization': `Bearer ${this.token}`,
    };

    const options = { method, headers };

    if (data && method !== 'GET') {
      headers['Content-Type'] = 'application/json';
      options.body = JSON.stringify(data);
    }

    const response = await fetch(`${BASE_URL}${endpoint}`, options);
    
    if (!response.ok) {
      throw new Error(`API call failed: ${response.status}`);
    }
    
    return await response.json();
  }

  // Get modules
  async getModules() {
    return this.apiCall('/modules');
  }

  // Send chat message
  async sendMessage(message, moduleId = 1) {
    return this.apiCall('/chat/', 'POST', {
      message: message,
      module_id: moduleId
    });
  }

  // Get memory stats
  async getMemoryStats(userId) {
    return this.apiCall(`/memory/stats/${userId}`);
  }

  // Logout
  logout() {
    this.token = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }
}

export default new ApiService();
