import React from 'react';
import { toast } from 'react-toastify';

function TaskList({ tasks, onTaskUpdated, onRefresh }) {
  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'pending';
      case 'processing':
        return 'processing';
      case 'completed':
        return 'completed';
      case 'failed':
        return 'failed';
      default:
        return 'pending';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'pending':
        return 'Ожидает';
      case 'processing':
        return 'Обрабатывается';
      case 'completed':
        return 'Завершено';
      case 'failed':
        return 'Ошибка';
      default:
        return 'Неизвестно';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('ru-RU');
  };

  if (tasks.length === 0) {
    return (
      <div>
        <h3>Мои задачи</h3>
        <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
          <p>У вас пока нет задач. Загрузите файл для создания первой задачи.</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h3>Мои задачи</h3>
        <button className="btn" onClick={onRefresh}>
          Обновить
        </button>
      </div>
      
      <ul className="task-list">
        {tasks.map((task) => (
          <li key={task.id} className="task-item">
            <div className="task-info">
              <div className="task-filename">{task.filename}</div>
              <div style={{ fontSize: '14px', color: '#666', marginBottom: '8px' }}>
                Создано: {formatDate(task.created_at)}
              </div>
              <div style={{ fontSize: '14px', color: '#666', marginBottom: '8px' }}>
                Уровень: {task.target_level} | 
                Аугментация: {task.augment ? `${task.aug_factor}x` : 'Выключена'}
              </div>
              {task.initial_count !== null && task.total_count !== null && (
                <div style={{ fontSize: '14px', color: '#666' }}>
                  Записей: {task.initial_count} → {task.total_count}
                </div>
              )}
              {task.error_message && (
                <div style={{ fontSize: '14px', color: '#dc3545', marginTop: '8px' }}>
                  Ошибка: {task.error_message}
                </div>
              )}
            </div>
            <div className="task-actions">
              <span className={`task-status ${getStatusColor(task.status)}`}>
                {getStatusText(task.status)}
              </span>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default TaskList;
