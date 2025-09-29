-- Примеры данных для тестирования системы

-- Вставка ролей
INSERT INTO roles (name, description, permissions) VALUES
('admin', 'Администратор системы', '{"read": true, "write": true, "delete": true, "manage_users": true, "manage_policies": true}'),
('analyst', 'Аналитик данных', '{"read": true, "write": false, "delete": false, "manage_users": false, "manage_policies": false}'),
('researcher', 'Исследователь', '{"read": true, "write": false, "delete": false, "manage_users": false, "manage_policies": false}'),
('auditor', 'Аудитор', '{"read": true, "write": false, "delete": false, "manage_users": false, "manage_policies": false}');

-- Вставка пользователей (пароли захешированы для 'password123')
INSERT INTO users (username, email, password_hash, role) VALUES
('admin', 'admin@privacy-proxy.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8KzKz2', 'admin'),
('analyst1', 'analyst1@company.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8KzKz2', 'analyst'),
('researcher1', 'researcher1@university.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8KzKz2', 'researcher'),
('auditor1', 'auditor1@audit.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8KzKz2', 'auditor');

-- Вставка политик приватности
INSERT INTO privacy_policies (name, description, policy_type, parameters, created_by) VALUES
('K-Anonymity Basic', 'Базовая политика k-анонимности с k=5', 'k_anonymity', '{"k": 5, "quasi_identifiers": ["age", "zipcode", "gender"]}', (SELECT id FROM users WHERE username = 'admin')),
('L-Diversity Sensitive', 'Политика l-разнообразия для чувствительных данных', 'l_diversity', '{"l": 3, "sensitive_attribute": "disease", "quasi_identifiers": ["age", "zipcode"]}', (SELECT id FROM users WHERE username = 'admin')),
('Differential Privacy Aggregates', 'Дифференциальная приватность для агрегирующих запросов', 'differential_privacy', '{"epsilon": 1.0, "delta": 0.00001, "sensitivity": 1}', (SELECT id FROM users WHERE username = 'admin')),
('GDPR Compliance', 'Политика соответствия GDPR', 'k_anonymity', '{"k": 10, "quasi_identifiers": ["age", "location", "income"]}', (SELECT id FROM users WHERE username = 'admin'));

-- Создание тестовой таблицы с персональными данными
CREATE TABLE IF NOT EXISTS personal_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100),
    age INTEGER,
    gender VARCHAR(10),
    zipcode VARCHAR(10),
    income DECIMAL(10,2),
    disease VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Вставка тестовых данных
INSERT INTO personal_data (name, age, gender, zipcode, income, disease) VALUES
('Иван Петров', 25, 'М', '101000', 50000.00, 'Гипертония'),
('Мария Сидорова', 30, 'Ж', '101001', 60000.00, 'Диабет'),
('Алексей Козлов', 35, 'М', '101002', 70000.00, 'Астма'),
('Елена Морозова', 28, 'Ж', '101003', 55000.00, 'Гипертония'),
('Дмитрий Волков', 42, 'М', '101004', 80000.00, 'Диабет'),
('Анна Лебедева', 33, 'Ж', '101005', 65000.00, 'Астма'),
('Сергей Новиков', 29, 'М', '101006', 58000.00, 'Гипертония'),
('Ольга Федорова', 31, 'Ж', '101007', 62000.00, 'Диабет'),
('Михаил Соколов', 38, 'М', '101008', 75000.00, 'Астма'),
('Татьяна Попова', 27, 'Ж', '101009', 52000.00, 'Гипертония'),
('Андрей Васильев', 45, 'М', '101010', 85000.00, 'Диабет'),
('Наталья Семенова', 32, 'Ж', '101011', 68000.00, 'Астма'),
('Владимир Петухов', 26, 'М', '101012', 48000.00, 'Гипертония'),
('Светлана Орлова', 34, 'Ж', '101013', 72000.00, 'Диабет'),
('Игорь Макаров', 40, 'М', '101014', 78000.00, 'Астма');

-- Создание представления для анонимизированных данных
CREATE OR REPLACE VIEW anonymized_personal_data AS
SELECT 
    id,
    CASE 
        WHEN age < 30 THEN '18-29'
        WHEN age < 40 THEN '30-39'
        WHEN age < 50 THEN '40-49'
        ELSE '50+'
    END as age_group,
    gender,
    LEFT(zipcode, 3) || '**' as zipcode_masked,
    CASE 
        WHEN income < 50000 THEN 'Низкий'
        WHEN income < 70000 THEN 'Средний'
        ELSE 'Высокий'
    END as income_level,
    disease,
    created_at
FROM personal_data;

-- Создание функции для получения статистики
CREATE OR REPLACE FUNCTION get_privacy_stats()
RETURNS TABLE (
    total_queries BIGINT,
    anonymized_queries BIGINT,
    avg_execution_time DECIMAL,
    most_used_policy VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_queries,
        COUNT(CASE WHEN privacy_policy_applied IS NOT NULL THEN 1 END) as anonymized_queries,
        AVG(execution_time_ms) as avg_execution_time,
        (SELECT name FROM privacy_policies WHERE id = (
            SELECT privacy_policy_applied 
            FROM query_logs 
            WHERE privacy_policy_applied IS NOT NULL 
            GROUP BY privacy_policy_applied 
            ORDER BY COUNT(*) DESC 
            LIMIT 1
        )) as most_used_policy
    FROM query_logs;
END;
$$ LANGUAGE plpgsql;
