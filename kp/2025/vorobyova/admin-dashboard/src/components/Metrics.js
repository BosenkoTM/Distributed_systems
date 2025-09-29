import React from 'react';

function Metrics({ metrics }) {
  return (
    <div className="metrics-grid">
      <div className="metric-card">
        <div className="metric-value">{metrics.totalUsers}</div>
        <div className="metric-label">Всего пользователей</div>
      </div>
      
      <div className="metric-card">
        <div className="metric-value">{metrics.totalTasks}</div>
        <div className="metric-label">Всего задач</div>
      </div>
      
      <div className="metric-card">
        <div className="metric-value">{metrics.completedTasks}</div>
        <div className="metric-label">Завершенных задач</div>
      </div>
      
      <div className="metric-card">
        <div className="metric-value">{metrics.failedTasks}</div>
        <div className="metric-label">Неудачных задач</div>
      </div>
      
      <div className="metric-card">
        <div className="metric-value">{metrics.totalResults}</div>
        <div className="metric-label">Готовых результатов</div>
      </div>
      
      <div className="metric-card">
        <div className="metric-value">
          {metrics.totalTasks > 0 ? Math.round((metrics.completedTasks / metrics.totalTasks) * 100) : 0}%
        </div>
        <div className="metric-label">Успешность обработки</div>
      </div>
    </div>
  );
}

export default Metrics;
