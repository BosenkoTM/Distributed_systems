import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor для обработки ошибок
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Сервер ответил с кодом ошибки
      throw new Error(error.response.data.detail || 'Произошла ошибка сервера');
    } else if (error.request) {
      // Запрос был отправлен, но ответа не получено
      throw new Error('Сервер недоступен. Проверьте подключение к интернету.');
    } else {
      // Ошибка при настройке запроса
      throw new Error('Произошла ошибка при отправке запроса');
    }
  }
);

export const sessionService = {
  createSession: async (annotatorId) => {
    const response = await api.post('/sessions/create', {
      annotator_id: annotatorId
    });
    return response.data;
  },

  getSession: async (sessionId) => {
    const response = await api.get(`/sessions/${sessionId}`);
    return response.data;
  },

  switchReplica: async (sessionId, replica) => {
    const response = await api.put(`/sessions/${sessionId}/switch-replica?replica=${replica}`);
    return response.data;
  },

  updateActivity: async (sessionId) => {
    const response = await api.put(`/sessions/${sessionId}/update-activity`);
    return response.data;
  },

  endSession: async (sessionId) => {
    const response = await api.delete(`/sessions/${sessionId}`);
    return response.data;
  },

  listSessions: async (activeOnly = true) => {
    const response = await api.get(`/sessions/?active_only=${activeOnly}`);
    return response.data;
  }
};

export const labelingService = {
  createLabeledData: async (labeledData) => {
    const response = await api.post('/labeling/', labeledData);
    return response.data;
  },

  getLabeledDataBySession: async (sessionId, limit = 100, offset = 0) => {
    const response = await api.get(`/labeling/${sessionId}?limit=${limit}&offset=${offset}`);
    return response.data;
  },

  updateLabeledData: async (dataId, updateData) => {
    const response = await api.put(`/labeling/${dataId}`, updateData);
    return response.data;
  },

  batchLabeling: async (batchRequest) => {
    const response = await api.post('/labeling/batch', batchRequest);
    return response.data;
  },

  getConflicts: async (sessionId) => {
    const response = await api.get(`/labeling/conflicts/${sessionId}`);
    return response.data;
  },

  resolveConflict: async (resolution) => {
    const response = await api.post('/labeling/resolve-conflict', resolution);
    return response.data;
  },

  getLabelingStats: async (annotatorId) => {
    const response = await api.get(`/labeling/stats/${annotatorId}`);
    return response.data;
  }
};

export const fileService = {
  uploadFile: async (file, uploadedBy = 'anonymous') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('uploaded_by', uploadedBy);

    const response = await api.post('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  listFiles: async () => {
    const response = await api.get('/files/');
    return response.data;
  },

  getFileData: async (fileId, limit = 100, offset = 0) => {
    const response = await api.get(`/files/${fileId}/data?limit=${limit}&offset=${offset}`);
    return response.data;
  },

  updateFileProgress: async (fileId, processedRows) => {
    const response = await api.put(`/files/${fileId}/progress`, {
      processed_rows: processedRows
    });
    return response.data;
  },

  deleteFile: async (fileId) => {
    const response = await api.delete(`/files/${fileId}`);
    return response.data;
  }
};

export const monitoringService = {
  getHealth: async () => {
    const response = await api.get('/monitoring/health');
    return response.data;
  },

  getMetrics: async () => {
    const response = await api.get('/monitoring/metrics');
    return response.data;
  },

  getEvents: async (eventType = null, limit = 100) => {
    const params = new URLSearchParams();
    if (eventType) params.append('event_type', eventType);
    params.append('limit', limit.toString());
    
    const response = await api.get(`/monitoring/events?${params.toString()}`);
    return response.data;
  },

  getReplicaStatus: async () => {
    const response = await api.get('/monitoring/replicas/status');
    return response.data;
  },

  getSessionStats: async () => {
    const response = await api.get('/monitoring/sessions/stats');
    return response.data;
  },

  getConflictStats: async () => {
    const response = await api.get('/monitoring/conflicts/stats');
    return response.data;
  }
};

export default api;
