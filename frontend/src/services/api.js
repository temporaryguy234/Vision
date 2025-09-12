import axios from 'axios';

const baseURL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: `${baseURL}/api`,
  timeout: 30000,
});

// Add request interceptor for auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('auth_token');
      window.location.href = '/';
    }
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const apiService = {
  // Generic HTTP methods
  async get(url, config = {}) {
    const response = await api.get(url, config);
    return response.data;
  },

  async post(url, data = {}, config = {}) {
    const response = await api.post(url, data, config);
    return response.data;
  },

  async put(url, data = {}, config = {}) {
    const response = await api.put(url, data, config);
    return response.data;
  },

  async delete(url, config = {}) {
    const response = await api.delete(url, config);
    return response.data;
  },

  // Authentication
  async login(email, password) {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },

  async register(email, password, full_name) {
    const response = await api.post('/auth/register', { 
      email, 
      password, 
      full_name 
    });
    return response.data;
  },

  async googleAuth(token) {
    const response = await api.post('/auth/google', { token });
    return response.data;
  },

  async getCurrentUser() {
    const response = await api.get('/auth/me');
    return response.data;
  },

  // Subscriptions
  async getSubscriptionPlans() {
    const response = await api.get('/subscriptions/plans');
    return response.data;
  },

  async getCurrentSubscription() {
    const response = await api.get('/subscriptions/current');
    return response.data;
  },

  async upgradeSubscription(tier) {
    const response = await api.post('/subscriptions/upgrade', { tier });
    return response.data;
  },

  // Payments
  async createPaymentIntent(paymentData) {
    const response = await api.post('/payments/create-intent', paymentData);
    return response.data;
  },

  async confirmPayPalPayment(paymentId, payerId) {
    const response = await api.post('/payments/paypal/confirm', {
      payment_id: paymentId,
      payer_id: payerId
    });
    return response.data;
  },

  // Exports
  async createExport(templateId, currentState, exportFormat = 'MP4', resolution = '1080p') {
    const response = await api.post('/exports/create', {
      template_id: templateId,
      current_state: currentState,
      export_format: exportFormat,
      resolution: resolution
    });
    return response.data;
  },

  async getUserExports() {
    const response = await api.get('/exports');
    return response.data;
  },

  async deleteExport(exportId) {
    const response = await api.delete(`/exports/${exportId}`);
    return response.data;
  },
  // Template Upload and Management
  async uploadTemplate(formData) {
    const response = await api.post('/templates/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async importFromUrl(url) {
    const formData = new FormData();
    formData.append('url', url);
    
    const response = await api.post('/templates/import-url', formData);
    return response.data;
  },

  async getTemplates(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const response = await api.get(`/templates${queryString ? '?' + queryString : ''}`);
    return response.data;
  },

  async getTemplate(templateId) {
    const response = await api.get(`/templates/${templateId}`);
    return response.data;
  },

  async getTemplateData(templateId) {
    const response = await api.get(`/templates/${templateId}/data`);
    return response.data;
  },

  async uploadTemplatePreviews(templateId, { imageFile, videoFile }) {
    const form = new FormData();
    if (imageFile) form.append('image', imageFile);
    if (videoFile) form.append('video', videoFile);
    const response = await api.post(`/templates/${templateId}/previews`, form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },

  // Template Revisions
  async saveRevision(templateId, revisionData) {
    const response = await api.post(`/templates/${templateId}/revisions`, revisionData);
    return response.data;
  },

  async getRevisions(templateId, userId) {
    const response = await api.get(`/templates/${templateId}/revisions`);
    return response.data;
  },

  // AI Prompt Processing
  async processPrompt(templateId, promptData) {
    const response = await api.post(`/templates/${templateId}/prompt`, promptData);
    return response.data;
  },

  // Legacy endpoints for compatibility
  async createTemplate(templateData) {
    const response = await api.post('/templates', templateData);
    return response.data;
  },

  async updateTemplate(templateId, templateData) {
    const response = await api.put(`/templates/${templateId}`, templateData);
    return response.data;
  },

  async deleteTemplate(templateId) {
    const response = await api.delete(`/templates/${templateId}`);
    return response.data;
  },

  // Projects
  async createProject(projectData) {
    const response = await api.post('/projects', projectData);
    return response.data;
  },

  async getProjects(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const response = await api.get(`/projects${queryString ? '?' + queryString : ''}`);
    return response.data;
  },

  async getProject(projectId) {
    const response = await api.get(`/projects/${projectId}`);
    return response.data;
  },

  async updateProject(projectId, projectData) {
    const response = await api.put(`/projects/${projectId}`, projectData);
    return response.data;
  },

  // Exports
  async createExport(exportData) {
    const response = await api.post('/exports', exportData);
    return response.data;
  },

  async getExports(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const response = await api.get(`/exports${queryString ? '?' + queryString : ''}`);
    return response.data;
  },

  // Brand Kits
  async createBrandKit(brandKitData) {
    const response = await api.post('/brand-kits', brandKitData);
    return response.data;
  },

  async getBrandKits(userId) {
    const response = await api.get(`/brand-kits`);
    return response.data;
  }
};

export default api;