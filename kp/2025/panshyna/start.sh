#!/bin/bash

# Скрипт запуска упрощенной системы верификации SQL-запросов

echo "🚀 Запуск упрощенной системы верификации SQL-запросов"
echo "======================================================"

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

# Создание директорий для данных
echo "📁 Создание директорий для данных..."
mkdir -p data/logs
mkdir -p data/sandbox

# Остановка существующих контейнеров
echo "🛑 Остановка существующих контейнеров..."
sudo docker compose down

# Сборка и запуск контейнеров
echo "🔨 Сборка и запуск контейнеров..."
sudo docker compose up --build -d

# Ожидание запуска сервисов
echo "⏳ Ожидание запуска сервисов..."
sleep 20

# Проверка статуса контейнеров
echo "🔍 Проверка статуса контейнеров..."
sudo docker compose ps

# Инициализация базы данных
echo "🗄️  Инициализация базы данных..."
sudo docker compose exec backend python init_db.py

echo ""
echo "✅ Система успешно запущена!"
echo ""
echo "🌐 Доступные сервисы:"
echo "   • Frontend: http://localhost:3000"
echo "   • Backend API: http://localhost:8000"
echo "   • API Documentation: http://localhost:8000/docs"
echo "   • Health Check: http://localhost:8000/health"
echo ""
echo "🗄️  База данных:"
echo "   • PostgreSQL: localhost:5432"
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
