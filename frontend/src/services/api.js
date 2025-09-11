import axios from 'axios';

const baseURL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: `${baseURL}/api`,
  timeout: 30000,
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
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
    const response = await api.get(`/templates/${templateId}/revisions?user_id=${userId}`);
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
    const response = await api.get(`/brand-kits?user_id=${userId}`);
    return response.data;
  }
};

export default api;