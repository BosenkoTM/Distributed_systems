import React from 'react';

function TaskTable({ tasks }) {
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('ru-RU');
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'status-pending';
      case 'processing':
        return 'status-processing';
      case 'completed':
        return 'status-completed';
      case 'failed':
        return 'status-failed';
      default:
        return 'status-pending';
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

  return (
    <div className="table-container">
      <div style={{ padding: '20px', borderBottom: '1px solid #ddd' }}>
        <h3>Последние задачи</h3>
      </div>
      <table className="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Файл</th>
            <th>Пользователь</th>
            <th>Статус</th>
            <th>Записей</th>
            <th>Дата создания</th>
          </tr>
        </thead>
        <tbody>
          {tasks.map((task) => (
            <tr key={task.id}>
              <td>{task.id}</td>
              <td>{task.filename}</td>
              <td>User {task.user_id}</td>
              <td>
                <span className={`status-badge ${getStatusColor(task.status)}`}>
                  {getStatusText(task.status)}
                </span>
              </td>
              <td>
                {task.initial_count && task.total_count 
                  ? `${task.initial_count} → ${task.total_count}`
                  : '-'
                }
              </td>
              <td>{formatDate(task.created_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default TaskTable;
