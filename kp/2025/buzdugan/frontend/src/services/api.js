import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Создание экземпляра axios
const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 10000,
});

// Интерцептор для добавления токена авторизации
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

// Интерцептор для обработки ошибок
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API для аутентификации
export const authAPI = {
  login: (username, password) =>
    api.post('/auth/login', { username, password }).then(res => res.data),
  
  logout: () =>
    api.post('/auth/logout').then(res => res.data),
  
  getCurrentUser: () =>
    api.get('/auth/me').then(res => res.data),
  
  refreshToken: () =>
    api.post('/auth/refresh').then(res => res.data),
};

// API для политик приватности
export const privacyAPI = {
  getPolicies: () =>
    api.get('/privacy/policies').then(res => res.data),
  
  createPolicy: (policyData) =>
    api.post('/privacy/policies', policyData).then(res => res.data),
  
  updatePolicy: (policyId, policyData) =>
    api.put(`/privacy/policies/${policyId}`, policyData).then(res => res.data),
  
  deletePolicy: (policyId) =>
    api.delete(`/privacy/policies/${policyId}`).then(res => res.data),
  
  anonymizeData: (requestData) =>
    api.post('/privacy/anonymize', requestData).then(res => res.data),
  
  getPrivacyMetrics: () =>
    api.get('/privacy/metrics').then(res => res.data),
};

// API для выполнения запросов
export const queryAPI = {
  executeQuery: (queryData) =>
    api.post('/query/execute', queryData).then(res => res.data),
  
  validateQuery: (queryData) =>
    api.post('/query/validate', queryData).then(res => res.data),
  
  getQueryHistory: (limit = 50, offset = 0) =>
    api.get(`/query/history?limit=${limit}&offset=${offset}`).then(res => res.data),
  
  getAccessibleTables: () =>
    api.get('/query/tables').then(res => res.data),
  
  getTableSchema: (tableName) =>
    api.get(`/query/schema/${tableName}`).then(res => res.data),
};

// API для администрирования
export const adminAPI = {
  getUsers: (limit = 50, offset = 0) =>
    api.get(`/admin/users?limit=${limit}&offset=${offset}`).then(res => res.data),
  
  createUser: (userData) =>
    api.post('/admin/users', userData).then(res => res.data),
  
  updateUser: (userId, userData) =>
    api.put(`/admin/users/${userId}`, userData).then(res => res.data),
  
  deleteUser: (userId) =>
    api.delete(`/admin/users/${userId}`).then(res => res.data),
  
  getSystemStats: () =>
    api.get('/admin/stats').then(res => res.data),
  
  getSystemLogs: (logType = 'all', limit = 100, offset = 0) =>
    api.get(`/admin/logs?log_type=${logType}&limit=${limit}&offset=${offset}`).then(res => res.data),
  
  createBackup: () =>
    api.post('/admin/backup').then(res => res.data),
};

// API для мониторинга
export const monitoringAPI = {
  getHealthStatus: () =>
    api.get('/monitoring/health').then(res => res.data),
  
  getSystemMetrics: () =>
    api.get('/monitoring/metrics').then(res => res.data),
  
  getPerformanceMetrics: (timeRange = '1h') =>
    api.get(`/monitoring/performance?time_range=${timeRange}`).then(res => res.data),
  
  getPrivacyMetrics: (timeRange = '24h') =>
    api.get(`/monitoring/privacy-metrics?time_range=${timeRange}`).then(res => res.data),
  
  getActiveAlerts: () =>
    api.get('/monitoring/alerts').then(res => res.data),
  
  getDashboardData: () =>
    api.get('/monitoring/dashboard').then(res => res.data),
};

export default api;
