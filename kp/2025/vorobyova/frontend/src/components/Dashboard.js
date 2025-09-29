import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import FileUpload from './FileUpload';
import TaskList from './TaskList';
import ResultList from './ResultList';
import axios from 'axios';

function Dashboard() {
  const [activeTab, setActiveTab] = useState('upload');
  const [tasks, setTasks] = useState([]);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchTasks = async () => {
    try {
      const response = await axios.get('http://localhost:8002/tasks');
      setTasks(response.data.tasks);
    } catch (error) {
      console.error('Error fetching tasks:', error);
    }
  };

  const fetchResults = async () => {
    try {
      const response = await axios.get('http://localhost:8003/results');
      setResults(response.data.results);
    } catch (error) {
      console.error('Error fetching results:', error);
    }
  };

  useEffect(() => {
    fetchTasks();
    fetchResults();
    
    // Poll for updates every 5 seconds
    const interval = setInterval(() => {
      fetchTasks();
      fetchResults();
    }, 5000);
    
    return () => clearInterval(interval);
  }, []);

  const handleTaskCreated = (newTask) => {
    setTasks(prev => [newTask, ...prev]);
    toast.success('Задача создана успешно!');
  };

  const handleTaskUpdated = (updatedTask) => {
    setTasks(prev => prev.map(task => 
      task.id === updatedTask.id ? updatedTask : task
    ));
  };

  const handleResultCreated = (newResult) => {
    setResults(prev => [newResult, ...prev]);
  };

  return (
    <div className="container">
      <div className="card">
        <h1>Дашборд разметчика</h1>
        <p>Добро пожаловать в систему создания SQL датасетов. Загружайте файлы, отслеживайте прогресс обработки и скачивайте результаты.</p>
      </div>

      {/* Tabs */}
      <div className="card">
        <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
          <button
            className={`btn ${activeTab === 'upload' ? 'btn-success' : ''}`}
            onClick={() => setActiveTab('upload')}
          >
            Загрузить файл
          </button>
          <button
            className={`btn ${activeTab === 'tasks' ? 'btn-success' : ''}`}
            onClick={() => setActiveTab('tasks')}
          >
            Мои задачи ({tasks.length})
          </button>
          <button
            className={`btn ${activeTab === 'results' ? 'btn-success' : ''}`}
            onClick={() => setActiveTab('results')}
          >
            Результаты ({results.length})
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === 'upload' && (
          <FileUpload 
            onTaskCreated={handleTaskCreated}
            onTaskUpdated={handleTaskUpdated}
          />
        )}
        
        {activeTab === 'tasks' && (
          <TaskList 
            tasks={tasks}
            onTaskUpdated={handleTaskUpdated}
            onRefresh={fetchTasks}
          />
        )}
        
        {activeTab === 'results' && (
          <ResultList 
            results={results}
            onResultCreated={handleResultCreated}
            onRefresh={fetchResults}
          />
        )}
      </div>
    </div>
  );
}

export default Dashboard;
