import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
const API_BASE = `${BACKEND_URL}/api`;

// Create axios instance
const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API service functions
export const apiService = {
  // Templates
  async getTemplates(params = {}) {
    const response = await api.get('/templates', { params });
    return response.data;
  },

  async getTemplate(templateId) {
    const response = await api.get(`/templates/${templateId}`);
    return response.data;
  },

  async createTemplate(templateData) {
    const response = await api.post('/templates', templateData);
    return response.data;
  },

  async updateTemplate(templateId, templateData) {
    const response = await api.put(`/templates/${templateId}`, templateData);
    return response.data;
  },

  // Projects
  async getProjects(userId, params = {}) {
    const response = await api.get('/projects', { 
      params: { user_id: userId, ...params } 
    });
    return response.data;
  },

  async getProject(projectId) {
    const response = await api.get(`/projects/${projectId}`);
    return response.data;
  },

  async createProject(projectData) {
    const response = await api.post('/projects', projectData);
    return response.data;
  },

  async updateProject(projectId, projectData) {
    const response = await api.put(`/projects/${projectId}`, projectData);
    return response.data;
  },

  async deleteProject(projectId) {
    const response = await api.delete(`/projects/${projectId}`);
    return response.data;
  },

  // Natural Language Commands
  async parseCommand(commandData) {
    const response = await api.post('/commands/parse', commandData);
    return response.data;
  },

  // Exports
  async getExports(userId, params = {}) {
    const response = await api.get('/exports', { 
      params: { user_id: userId, ...params } 
    });
    return response.data;
  },

  async createExport(exportData) {
    const response = await api.post('/exports', exportData);
    return response.data;
  },

  // Brand Kits
  async getBrandKits(userId, params = {}) {
    const response = await api.get('/brand-kits', { 
      params: { user_id: userId, ...params } 
    });
    return response.data;
  },

  async createBrandKit(brandKitData) {
    const response = await api.post('/brand-kits', brandKitData);
    return response.data;
  },

  async deleteBrandKit(kitId) {
    const response = await api.delete(`/brand-kits/${kitId}`);
    return response.data;
  },

  // Statistics
  async getStats() {
    const response = await api.get('/stats');
    return response.data;
  },

  // File Upload
  async uploadTemplate(formData) {
    const response = await api.post('/upload/template', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Bulk Import
  async bulkImportUpload(formData) {
    const response = await api.post('/bulk-import/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async bulkImportCreateTemplates(templateData) {
    const response = await api.post('/bulk-import/create-templates', templateData);
    return response.data;
  },
};

// Error interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export default api;