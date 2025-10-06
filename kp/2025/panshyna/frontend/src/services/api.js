import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor для обработки ошибок
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Произошла ошибка сервера');
    } else if (error.request) {
      throw new Error('Сервер недоступен. Проверьте подключение к интернету.');
    } else {
      throw new Error('Произошла ошибка при отправке запроса');
    }
  }
);

export const sqlService = {
  executeSQL: async (sqlQuery, timeout = 30) => {
    const response = await api.post('/sql/execute', {
      sql_query: sqlQuery,
      timeout: timeout
    });
    return response.data;
  },

  validateSQL: async (queryId) => {
    const response = await api.get(`/sql/validate/${queryId}`);
    return response.data;
  }
};

export const taskService = {
  createTask: async (taskData) => {
    const response = await api.post('/tasks/', taskData);
    return response.data;
  },

  getTasks: async () => {
    const response = await api.get('/tasks/');
    return response.data;
  },

  getTask: async (taskId) => {
    const response = await api.get(`/tasks/${taskId}`);
    return response.data;
  },

  executeTask: async (taskId) => {
    const response = await api.post(`/tasks/${taskId}/execute`);
    return response.data;
  }
};

export const verificationService = {
  createVerification: async (verificationData) => {
    const response = await api.post('/verifications/', verificationData);
    return response.data;
  },

  getTaskVerifications: async (taskId) => {
    const response = await api.get(`/verifications/task/${taskId}`);
    return response.data;
  }
};

export const monitoringService = {
  getStats: async () => {
    const response = await api.get('/monitoring/stats');
    return response.data;
  },

  getLogs: async (limit = 100) => {
    const response = await api.get(`/monitoring/logs?limit=${limit}`);
    return response.data;
  },

  getHealth: async () => {
    const response = await api.get('/health');
    return response.data;
  }
};

export const initService = {
  initDatabase: async () => {
    const response = await api.post('/init');
    return response.data;
  }
};

export default api;
