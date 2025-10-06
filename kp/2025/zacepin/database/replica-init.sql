-- Инициализация реплики (выполняется автоматически при создании реплики)
-- Этот файл содержит команды, которые будут выполнены после создания реплики

-- Создание индексов для оптимизации чтения на репликах
CREATE INDEX IF NOT EXISTS idx_labeled_data_read_optimized ON labeled_data(session_id, created_at);
CREATE INDEX IF NOT EXISTS idx_annotator_sessions_read_optimized ON annotator_sessions(is_active, last_activity);

-- Создание представления для быстрого доступа к статистике
CREATE OR REPLACE VIEW replica_stats AS
SELECT 
    'replica' as node_type,
    COUNT(*) as total_records,
    COUNT(CASE WHEN is_conflict = TRUE THEN 1 END) as conflict_records,
    MAX(updated_at) as last_update
FROM labeled_data;
