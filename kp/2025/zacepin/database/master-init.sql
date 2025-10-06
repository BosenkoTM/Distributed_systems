-- Создание пользователя для репликации
CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'replicator';

-- Создание базы данных для системы разметки
CREATE DATABASE labeling_db;

-- Подключение к базе данных
\c labeling_db;

-- Создание таблицы для хранения данных разметки
CREATE TABLE labeled_data (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    annotator_id VARCHAR(255) NOT NULL,
    data_id VARCHAR(255) NOT NULL,
    original_text TEXT NOT NULL,
    label VARCHAR(255) NOT NULL,
    confidence DECIMAL(3,2) DEFAULT 0.0,
    vector_clock JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_conflict BOOLEAN DEFAULT FALSE,
    conflict_resolution VARCHAR(50) DEFAULT 'pending'
);

-- Создание таблицы для отслеживания сессий
CREATE TABLE annotator_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    annotator_id VARCHAR(255) NOT NULL,
    current_replica VARCHAR(50) DEFAULT 'master',
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы для vector clocks
CREATE TABLE vector_clocks (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    clock_data JSONB NOT NULL,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы для CSV файлов
CREATE TABLE csv_files (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    total_rows INTEGER NOT NULL,
    processed_rows INTEGER DEFAULT 0,
    uploaded_by VARCHAR(255) NOT NULL,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'uploaded'
);

-- Создание индексов для оптимизации запросов
CREATE INDEX idx_labeled_data_session ON labeled_data(session_id);
CREATE INDEX idx_labeled_data_annotator ON labeled_data(annotator_id);
CREATE INDEX idx_labeled_data_created_at ON labeled_data(created_at);
CREATE INDEX idx_annotator_sessions_active ON annotator_sessions(is_active);
CREATE INDEX idx_vector_clocks_session ON vector_clocks(session_id);

-- Создание функции для обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Создание триггера для автоматического обновления updated_at
CREATE TRIGGER update_labeled_data_updated_at 
    BEFORE UPDATE ON labeled_data 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Вставка тестовых данных
INSERT INTO csv_files (filename, file_path, total_rows, uploaded_by) VALUES
('sample_data.csv', '/data/sample_data.csv', 1000, 'admin'),
('test_dataset.csv', '/data/test_dataset.csv', 500, 'admin');

-- Создание представления для статистики
CREATE VIEW labeling_stats AS
SELECT 
    a.annotator_id,
    COUNT(ld.id) as total_labels,
    COUNT(CASE WHEN ld.is_conflict = TRUE THEN 1 END) as conflicts,
    AVG(ld.confidence) as avg_confidence,
    MAX(ld.updated_at) as last_activity
FROM annotator_sessions a
LEFT JOIN labeled_data ld ON a.session_id = ld.session_id
WHERE a.is_active = TRUE
GROUP BY a.annotator_id;
