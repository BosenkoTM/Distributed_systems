#!/bin/bash

# Скрипт для быстрого запуска федеративного обучения

echo "=========================================="
echo "Запуск федеративного обучения на CIFAR-10"
echo "=========================================="

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен"
    exit 1
fi

echo "✅ Docker и Docker Compose найдены"

# Создание директорий
mkdir -p shared results data
echo "✅ Директории созданы"

# Запуск сервисов
echo "🚀 Запуск сервисов..."
docker-compose up -d --build

# Ожидание готовности сервера
echo "⏳ Ожидание готовности сервера..."
sleep 30

# Проверка статуса
echo "📊 Статус сервисов:"
docker-compose ps

echo ""
echo "=========================================="
echo "Система запущена!"
echo "=========================================="
echo ""
echo "Для мониторинга используйте:"
echo "  docker-compose logs -f federated-server"
echo "  docker-compose logs -f client-1"
echo ""
echo "Для остановки:"
echo "  docker-compose down"
echo ""
echo "Результаты будут сохранены в директории 'results/'"
echo "=========================================="
