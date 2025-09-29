import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import Metrics from './Metrics';
import TaskChart from './TaskChart';
import UserTable from './UserTable';
import TaskTable from './TaskTable';
import axios from 'axios';

function Dashboard() {
  const [metrics, setMetrics] = useState({
    totalUsers: 0,
    totalTasks: 0,
    completedTasks: 0,
    failedTasks: 0,
    totalResults: 0
  });
  const [users, setUsers] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchMetrics = async () => {
    try {
      // Fetch users
      const usersResponse = await axios.get('/users');
      const totalUsers = usersResponse.data.length;

      // Fetch tasks (we'll need to implement this endpoint)
      // For now, we'll use mock data
      const totalTasks = 150;
      const completedTasks = 120;
      const failedTasks = 5;
      const totalResults = 115;

      setMetrics({
        totalUsers,
        totalTasks,
        completedTasks,
        failedTasks,
        totalResults
      });

      setUsers(usersResponse.data);
    } catch (error) {
      console.error('Error fetching metrics:', error);
      toast.error('Ошибка при загрузке метрик');
    }
  };

  const fetchTasks = async () => {
    try {
      // This would be implemented when we have a proper admin endpoint
      // For now, we'll use mock data
      const mockTasks = [
        {
          id: '1',
          filename: 'dataset1.xlsx',
          status: 'completed',
          user_id: 1,
          created_at: new Date().toISOString(),
          initial_count: 100,
          total_count: 150
        },
        {
          id: '2',
          filename: 'dataset2.csv',
          status: 'processing',
          user_id: 2,
          created_at: new Date().toISOString(),
          initial_count: null,
          total_count: null
        }
      ];
      setTasks(mockTasks);
    } catch (error) {
      console.error('Error fetching tasks:', error);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchMetrics(), fetchTasks()]);
      setLoading(false);
    };

    loadData();

    // Set up real-time updates
    const interval = setInterval(() => {
      fetchMetrics();
      fetchTasks();
    }, 10000); // Update every 10 seconds

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="container">
        <div className="loading">
          <div className="spinner"></div>
          Загрузка дашборда...
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="card">
        <h1>
          <span className="realtime-indicator"></span>
          Админский дашборд
        </h1>
        <p>Мониторинг системы в реальном времени</p>
      </div>

      <Metrics metrics={metrics} />
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
        <TaskChart tasks={tasks} />
        <div className="card">
          <h3>Статус системы</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>База данных:</span>
              <span style={{ color: '#28a745' }}>● Онлайн</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>RabbitMQ:</span>
              <span style={{ color: '#28a745' }}>● Онлайн</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Сервис пользователей:</span>
              <span style={{ color: '#28a745' }}>● Онлайн</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Сервис задач:</span>
              <span style={{ color: '#28a745' }}>● Онлайн</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Сервис результатов:</span>
              <span style={{ color: '#28a745' }}>● Онлайн</span>
            </div>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <UserTable users={users} />
        <TaskTable tasks={tasks} />
      </div>
    </div>
  );
}

export default Dashboard;
