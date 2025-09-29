import React from 'react';
import { toast } from 'react-toastify';
import axios from 'axios';

function ResultList({ results, onResultCreated, onRefresh }) {
  const handleDownload = async (resultId, filename) => {
    try {
      const response = await axios.get(`http://localhost:8003/results/${resultId}/download`, {
        responseType: 'blob',
      });
      
      // Create blob link to download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success('Файл скачан успешно!');
    } catch (error) {
      console.error('Download error:', error);
      toast.error('Ошибка при скачивании файла');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('ru-RU');
  };

  if (results.length === 0) {
    return (
      <div>
        <h3>Результаты</h3>
        <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
          <p>У вас пока нет готовых результатов. Дождитесь завершения обработки задач.</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h3>Результаты</h3>
        <button className="btn" onClick={onRefresh}>
          Обновить
        </button>
      </div>
      
      <ul className="task-list">
        {results.map((result) => (
          <li key={result.id} className="task-item">
            <div className="task-info">
              <div className="task-filename">{result.filename}</div>
              <div style={{ fontSize: '14px', color: '#666', marginBottom: '8px' }}>
                Создано: {formatDate(result.created_at)}
              </div>
              {result.initial_count !== null && result.total_count !== null && (
                <div style={{ fontSize: '14px', color: '#666' }}>
                  Записей: {result.initial_count} → {result.total_count}
                </div>
              )}
            </div>
            <div className="task-actions">
              <span className={`task-status ${result.status === 'completed' ? 'completed' : 'pending'}`}>
                {result.status === 'completed' ? 'Готово' : 'Обрабатывается'}
              </span>
              {result.status === 'completed' && (
                <button
                  className="btn btn-success"
                  onClick={() => handleDownload(result.id, result.filename)}
                  style={{ marginLeft: '10px' }}
                >
                  Скачать
                </button>
              )}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default ResultList;
