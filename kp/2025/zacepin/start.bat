@echo off
echo 🚀 Запуск системы клиент-центричной согласованности для разметчиков
echo ==================================================================

REM Проверка наличия Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker не установлен. Пожалуйста, установите Docker Desktop.
    pause
    exit /b 1
)

docker compose version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose V2 не установлен. Пожалуйста, установите Docker Compose V2.
    pause
    exit /b 1
)

REM Создание директории для данных
echo 📁 Создание директорий для данных...
if not exist "backend\data" mkdir backend\data
if not exist "database\backups" mkdir database\backups

REM Остановка существующих контейнеров
echo 🛑 Остановка существующих контейнеров...
docker compose down

REM Сборка и запуск контейнеров
echo 🔨 Сборка и запуск контейнеров...
docker compose up --build -d

REM Ожидание запуска сервисов
echo ⏳ Ожидание запуска сервисов...
timeout /t 30 /nobreak >nul

REM Проверка статуса контейнеров
echo 🔍 Проверка статуса контейнеров...
docker compose ps

REM Инициализация базы данных
echo 🗄️  Инициализация базы данных...
docker compose exec backend python init_db.py

REM Запуск тестов
echo 🧪 Запуск тестов...
docker compose exec backend pytest tests/ -v

echo.
echo ✅ Система успешно запущена!
echo.
echo 🌐 Доступные сервисы:
echo    • Frontend: http://localhost:3000
echo    • Backend API: http://localhost:8000
echo    • API Documentation: http://localhost:8000/docs
echo    • Nginx (Load Balancer): http://localhost:80
echo.
echo 📊 Мониторинг:
echo    • Health Check: http://localhost:8000/health
echo    • Metrics: http://localhost:8000/api/v1/monitoring/metrics
echo.
echo 🗄️  База данных:
echo    • PostgreSQL Master: localhost:5432
echo    • PostgreSQL Replica 1: localhost:5433
echo    • PostgreSQL Replica 2: localhost:5434
echo    • Redis: localhost:6379
echo.
echo 📝 Логи:
echo    • Просмотр логов: docker compose logs -f
echo    • Логи backend: docker compose logs -f backend
echo    • Логи frontend: docker compose logs -f frontend
echo.
echo 🛑 Остановка системы:
echo    • docker compose down
echo.
echo 🔄 Перезапуск:
echo    • docker compose restart
echo.
echo 🎉 Готово к работе!
pause
