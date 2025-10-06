#!/bin/bash

# Скрипт запуска системы разметки

echo "🚀 Запуск системы клиент-центричной согласованности для разметчиков"
echo "=================================================================="

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Пожалуйста, установите Docker."
    exit 1
fi

# Проверка Docker Compose V2
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose V2 не установлен. Пожалуйста, установите Docker Compose V2."
    exit 1
fi

# Создание директории для данных
echo "📁 Создание директорий для данных..."
mkdir -p backend/data
mkdir -p database/backups

# Остановка существующих контейнеров
echo "🛑 Остановка существующих контейнеров..."
sudo docker compose down

# Сборка и запуск контейнеров
echo "🔨 Сборка и запуск контейнеров..."
sudo docker compose up --build -d

# Ожидание запуска сервисов
echo "⏳ Ожидание запуска сервисов..."
sleep 30

# Проверка статуса контейнеров
echo "🔍 Проверка статуса контейнеров..."
sudo docker compose ps

# Инициализация базы данных
echo "🗄️  Инициализация базы данных..."
sudo docker compose exec backend python init_db.py

# Запуск тестов
echo "🧪 Запуск тестов..."
sudo docker compose exec backend pytest tests/ -v

echo ""
echo "✅ Система успешно запущена!"
echo ""
echo "🌐 Доступные сервисы:"
echo "   • Frontend: http://localhost:3000"
echo "   • Backend API: http://localhost:8000"
echo "   • API Documentation: http://localhost:8000/docs"
echo "   • Nginx (Load Balancer): http://localhost:80"
echo ""
echo "📊 Мониторинг:"
echo "   • Health Check: http://localhost:8000/health"
echo "   • Metrics: http://localhost:8000/api/v1/monitoring/metrics"
echo ""
echo "🗄️  База данных:"
echo "   • PostgreSQL Master: localhost:5432"
echo "   • PostgreSQL Replica 1: localhost:5433"
echo "   • PostgreSQL Replica 2: localhost:5434"
echo "   • Redis: localhost:6379"
echo ""
echo "📝 Логи:"
echo "   • Просмотр логов: sudo docker compose logs -f"
echo "   • Логи backend: sudo docker compose logs -f backend"
echo "   • Логи frontend: sudo docker compose logs -f frontend"
echo ""
echo "🛑 Остановка системы:"
echo "   • sudo docker compose down"
echo ""
echo "🔄 Перезапуск:"
echo "   • sudo docker compose restart"
echo ""
echo "🎉 Готово к работе!"
