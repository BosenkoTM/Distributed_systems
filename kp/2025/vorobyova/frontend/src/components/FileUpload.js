import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { toast } from 'react-toastify';
import axios from 'axios';

function FileUpload({ onTaskCreated, onTaskUpdated }) {
  const [uploading, setUploading] = useState(false);
  const [settings, setSettings] = useState({
    target_level: 'Автоматически',
    augment: false,
    aug_factor: 1
  });

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;

    // Validate file type
    if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.csv')) {
      toast.error('Поддерживаются только файлы .xlsx и .csv');
      return;
    }

    setUploading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('target_level', settings.target_level);
      formData.append('augment', settings.augment);
      formData.append('aug_factor', settings.aug_factor);

      const response = await axios.post('http://localhost:8002/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      onTaskCreated(response.data);
      toast.success('Файл загружен успешно! Обработка начата.');
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Ошибка при загрузке файла: ' + (error.response?.data?.detail || 'Неизвестная ошибка'));
    } finally {
      setUploading(false);
    }
  }, [settings, onTaskCreated]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'text/csv': ['.csv']
    },
    multiple: false,
    disabled: uploading
  });

  const handleSettingChange = (key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  return (
    <div>
      <h3>Загрузка файла</h3>
      
      {/* Settings */}
      <div style={{ marginBottom: '30px' }}>
        <h4>Настройки обработки</h4>
        
        <div className="form-group">
          <label className="form-label">Целевой уровень сложности:</label>
          <select
            className="form-control"
            value={settings.target_level}
            onChange={(e) => handleSettingChange('target_level', e.target.value)}
          >
            <option value="Автоматически">Автоматически</option>
            <option value="Beginner">Beginner</option>
            <option value="Intermediate">Intermediate</option>
            <option value="Advanced">Advanced</option>
            <option value="Expert">Expert</option>
          </select>
        </div>

        <div className="form-group">
          <div className="checkbox-group">
            <input
              type="checkbox"
              id="augment"
              checked={settings.augment}
              onChange={(e) => handleSettingChange('augment', e.target.checked)}
            />
            <label htmlFor="augment">Включить аугментацию</label>
          </div>
        </div>

        {settings.augment && (
          <div className="form-group">
            <label className="form-label">
              Коэффициент увеличения: {settings.aug_factor}x
            </label>
            <input
              type="range"
              min="1"
              max="5"
              value={settings.aug_factor}
              onChange={(e) => handleSettingChange('aug_factor', parseInt(e.target.value))}
              className="slider"
            />
            <div className="slider-label">
              Увеличит количество записей в {settings.aug_factor} раз
            </div>
          </div>
        )}
      </div>

      {/* Upload Area */}
      <div
        {...getRootProps()}
        className={`upload-area ${isDragActive ? 'dragover' : ''}`}
        style={{ opacity: uploading ? 0.6 : 1, cursor: uploading ? 'not-allowed' : 'pointer' }}
      >
        <input {...getInputProps()} />
        <div className="upload-icon">📁</div>
        <div className="upload-text">
          {isDragActive
            ? 'Отпустите файл здесь...'
            : 'Перетащите файл сюда или нажмите для выбора'
          }
        </div>
        <div className="upload-hint">
          Поддерживаются файлы .xlsx и .csv
        </div>
        {uploading && (
          <div style={{ marginTop: '20px' }}>
            <div className="spinner"></div>
            <div>Загрузка и обработка файла...</div>
          </div>
        )}
      </div>

      {/* File Format Info */}
      <div className="card" style={{ marginTop: '20px', backgroundColor: '#f8f9fa' }}>
        <h4>Формат файла</h4>
        <p>Файл должен содержать следующие колонки:</p>
        <ul>
          <li><strong>id</strong> - уникальный идентификатор записи</li>
          <li><strong>domain</strong> - домен задачи</li>
          <li><strong>sql_complexity</strong> - уровень сложности (Beginner, Intermediate, Advanced, Expert)</li>
          <li><strong>sql_prompt</strong> - описание задачи на естественном языке</li>
          <li><strong>sql</strong> - SQL запрос</li>
          <li><strong>sql_explanation</strong> - объяснение SQL запроса</li>
          <li><strong>sql_context</strong> - контекст (схема БД)</li>
        </ul>
        <p><em>Дополнительно можно добавить колонки с вариациями для аугментации: prompt_variation_1, sql_variation_1, и т.д.</em></p>
      </div>
    </div>
  );
}

export default FileUpload;
