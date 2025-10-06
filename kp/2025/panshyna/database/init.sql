-- Инициализация базы данных для системы верификации SQL-запросов

-- Создание таблицы задач
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    sql_query TEXT NOT NULL,
    expected_result TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    result TEXT,
    execution_time FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Создание таблицы верификаций
CREATE TABLE IF NOT EXISTS verifications (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks(id),
    verifier_name VARCHAR(100) NOT NULL,
    is_correct BOOLEAN NOT NULL,
    confidence FLOAT NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание индексов для оптимизации
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at);
CREATE INDEX IF NOT EXISTS idx_verifications_task_id ON verifications(task_id);
CREATE INDEX IF NOT EXISTS idx_verifications_created_at ON verifications(created_at);

-- Вставка тестовых данных
INSERT INTO tasks (title, description, sql_query, expected_result) VALUES
('Простой SELECT запрос', 'Выбрать все записи из таблицы users', 'SELECT * FROM users LIMIT 10;', 'Список пользователей'),
('Запрос с WHERE', 'Выбрать активных пользователей', 'SELECT name, email FROM users WHERE active = true;', 'Активные пользователи'),
('Агрегатный запрос', 'Подсчитать количество пользователей', 'SELECT COUNT(*) as user_count FROM users;', 'Общее количество пользователей')
ON CONFLICT DO NOTHING;

-- Создание представления для статистики
CREATE OR REPLACE VIEW task_stats AS
SELECT 
    status,
    COUNT(*) as count,
    AVG(execution_time) as avg_execution_time,
    MAX(created_at) as last_created
FROM tasks
GROUP BY status;

-- Создание представления для статистики верификаций
CREATE OR REPLACE VIEW verification_stats AS
SELECT 
    t.id as task_id,
    t.title as task_title,
    COUNT(v.id) as verification_count,
    COUNT(CASE WHEN v.is_correct = true THEN 1 END) as correct_count,
    COUNT(CASE WHEN v.is_correct = false THEN 1 END) as incorrect_count,
    AVG(v.confidence) as avg_confidence
FROM tasks t
LEFT JOIN verifications v ON t.id = v.task_id
GROUP BY t.id, t.title;
