#!/bin/bash

# SQL Dataset Generator - Скрипт запуска
echo "🚀 Запуск SQL Dataset Generator..."

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Пожалуйста, установите Docker и попробуйте снова."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен. Пожалуйста, установите Docker Compose и попробуйте снова."
    exit 1
fi

# Создание необходимых директорий
echo "📁 Создание директорий..."
mkdir -p uploads results

# Запуск сервисов
echo "🐳 Запуск Docker контейнеров..."
docker-compose up -d

# Ожидание запуска сервисов
echo "⏳ Ожидание запуска сервисов..."
sleep 10

# Проверка статуса сервисов
echo "🔍 Проверка статуса сервисов..."
docker-compose ps

echo ""
echo "✅ Сервисы запущены!"
echo ""
echo "🌐 Доступные адреса:"
echo "   Основное приложение: http://localhost:3000"
echo "   Админский дашборд:   http://localhost:3001"
echo "   RabbitMQ Management: http://localhost:15672 (admin/admin)"
echo ""
echo "📚 API документация:"
echo "   User Service:   http://localhost:8001/docs"
echo "   Task Service:   http://localhost:8002/docs"
echo "   Result Service: http://localhost:8003/docs"
echo ""
echo "🛑 Для остановки сервисов выполните: docker-compose down"
echo ""
