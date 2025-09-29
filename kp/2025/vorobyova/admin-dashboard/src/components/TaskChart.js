import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

function TaskChart({ tasks }) {
  // Mock data for the chart
  const chartData = [
    { name: 'Пн', tasks: 12, completed: 10 },
    { name: 'Вт', tasks: 15, completed: 13 },
    { name: 'Ср', tasks: 8, completed: 7 },
    { name: 'Чт', tasks: 20, completed: 18 },
    { name: 'Пт', tasks: 18, completed: 16 },
    { name: 'Сб', tasks: 5, completed: 4 },
    { name: 'Вс', tasks: 3, completed: 3 }
  ];

  return (
    <div className="chart-container">
      <h3 className="chart-title">Статистика задач по дням</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Line 
            type="monotone" 
            dataKey="tasks" 
            stroke="#007bff" 
            strokeWidth={2}
            name="Всего задач"
          />
          <Line 
            type="monotone" 
            dataKey="completed" 
            stroke="#28a745" 
            strokeWidth={2}
            name="Завершено"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default TaskChart;
