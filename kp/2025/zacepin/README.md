# Клиент-центричная модель согласованности для разметчиков

## Описание проекта

Система для работы разметчиков с локальными данными (CSV) и синхронизации с распределенной базой данных PostgreSQL. Реализует клиент-центричную модель согласованности с использованием vector clocks для разрешения конфликтов.

## Архитектура системы

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React.js      │    │   React.js      │    │   React.js      │
│   Frontend      │    │   Frontend      │    │   Frontend      │
│   (Разметчик 1) │    │   (Разметчик 2) │    │   (Разметчик N) │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │      FastAPI Backend      │
                    │   (Session Manager)       │
                    │  - Vector Clocks          │
                    │  - Conflict Resolution    │
                    │  - Load Balancing         │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │    PostgreSQL Master      │
                    │   (Primary Database)      │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │   PostgreSQL Replicas     │
                    │  (Read-only replicas)     │
                    └───────────────────────────┘
```

## Технологический стек

### Backend
- **Python 3.9+** - основной язык
- **FastAPI** - веб-фреймворк для API
- **SQLAlchemy** - ORM для работы с БД
- **PostgreSQL** - основная база данных
- **Redis** - кэширование и сессии
- **Pydantic** - валидация данных

### Frontend
- **React.js 18** - пользовательский интерфейс
- **Axios** - HTTP клиент
- **Material-UI** - компоненты интерфейса
- **React Router** - маршрутизация

### Инфраструктура
- **Docker & Docker Compose** - контейнеризация
- **Nginx** - reverse proxy и load balancer
- **Pytest** - тестирование

## Пошаговое решение задачи

### 1. Настройка инфраструктуры
- Создание Docker-контейнеров для PostgreSQL master-slave
- Настройка репликации между узлами БД
- Конфигурация Nginx для балансировки нагрузки

### 2. Backend разработка
- Реализация FastAPI приложения с управлением сессиями
- Создание системы vector clocks для отслеживания временных меток
- Разработка алгоритмов разрешения конфликтов
- API для работы с CSV данными и разметкой

### 3. Frontend разработка
- Создание React приложения для разметчиков
- Интерфейс загрузки и обработки CSV файлов
- Система разметки данных с сохранением в БД
- Отображение статуса синхронизации

### 4. Система согласованности
- Реализация клиент-центричной модели
- Отслеживание сессий разметчиков
- Автоматическое переключение между репликами
- Обработка конфликтов при одновременной работе

### 5. Тестирование
- Unit тесты для компонентов системы
- Integration тесты для проверки согласованности
- Load тесты для проверки производительности
- Тесты сценариев с задержками репликации

### 6. Мониторинг и логирование
- Система логирования всех операций
- Мониторинг состояния реплик
- Метрики производительности
- Алерты при нарушениях согласованности

## Требования

### Ubuntu/Linux
- Docker Engine 20.10+
- Docker Compose V2 (встроен в Docker Desktop)
- Python 3.9+ (для локальной разработки)
- Node.js 18+ (для локальной разработки)

### Windows
- Docker Desktop 4.0+
- Python 3.9+ (для локальной разработки)
- Node.js 18+ (для локальной разработки)

### Установка Docker на Ubuntu

Подробные инструкции по установке Docker на Ubuntu см. в файле [UBUNTU_SETUP.md](UBUNTU_SETUP.md).

Краткая установка:
```bash
# Обновление пакетов
sudo apt update

# Установка зависимостей
sudo apt install apt-transport-https ca-certificates curl gnupg lsb-release

# Добавление GPG ключа Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Добавление репозитория Docker
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Установка Docker
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER

# Перезагрузка для применения изменений
sudo systemctl enable docker
sudo systemctl start docker
```

## Запуск проекта

### Быстрый запуск

**Windows:**
```cmd
# Запуск скрипта
start.bat
```

**Linux/macOS (Ubuntu):**
```bash
# Запуск скрипта
chmod +x start.sh
./start.sh
```

### Ручной запуск

**Ubuntu/Linux:**
```bash
# Переход в директорию проекта
cd zacepin

# Создание директорий для данных
mkdir -p backend/data database/backups

# Запуск всех сервисов
sudo docker compose up --build -d

# Ожидание запуска (30 секунд)
sleep 30

# Инициализация базы данных
sudo docker compose exec backend python init_db.py

# Запуск тестов
sudo docker compose exec backend pytest tests/ -v
```

**Windows:**
```cmd
# Переход в директорию проекта
cd zacepin

# Создание директорий для данных
mkdir backend\data
mkdir database\backups

# Запуск всех сервисов
docker compose up --build -d

# Ожидание запуска (30 секунд)
timeout /t 30 /nobreak

# Инициализация базы данных
docker compose exec backend python init_db.py

# Запуск тестов
docker compose exec backend pytest tests/ -v
```

### Доступ к приложению

- **Frontend (React)**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Nginx Load Balancer**: http://localhost:80
- **Health Check**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/api/v1/monitoring/metrics

### База данных

- **PostgreSQL Master**: localhost:5432
- **PostgreSQL Replica 1**: localhost:5433  
- **PostgreSQL Replica 2**: localhost:5434
- **Redis**: localhost:6379

### Управление системой

**Ubuntu/Linux:**
```bash
# Просмотр логов
sudo docker compose logs -f

# Остановка системы
sudo docker compose down

# Перезапуск
sudo docker compose restart

# Пересборка
sudo docker compose up --build -d
```

**Windows:**
```cmd
# Просмотр логов
docker compose logs -f

# Остановка системы
docker compose down

# Перезапуск
docker compose restart

# Пересборка
docker compose up --build -d
```

## Структура проекта

```
zacepin/
├── backend/                 # FastAPI приложение
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Конфигурация и настройки
│   │   ├── models/         # SQLAlchemy модели
│   │   ├── services/       # Бизнес-логика
│   │   └── utils/          # Утилиты (vector clocks)
│   ├── tests/              # Тесты
│   └── requirements.txt
├── frontend/               # React приложение
│   ├── src/
│   │   ├── components/     # React компоненты
│   │   ├── services/       # API клиенты
│   │   └── utils/          # Утилиты
│   └── package.json
├── database/               # SQL скрипты
├── docker-compose.yml      # Конфигурация контейнеров
└── README.md
```

## Ключевые особенности

1. **Клиент-центричная согласованность** - каждый разметчик работает с локальной копией данных
2. **Vector Clocks** - точное отслеживание порядка операций
3. **Автоматическое разрешение конфликтов** - при обнаружении противоречий
4. **Горизонтальное масштабирование** - поддержка множественных реплик
5. **Fault tolerance** - автоматическое переключение при сбоях
6. **Real-time синхронизация** - обновления в реальном времени

## Тестирование

### Запуск тестов

**Ubuntu/Linux:**
```bash
# Все тесты
sudo docker compose exec backend pytest tests/ -v

# Тесты согласованности
sudo docker compose exec backend pytest tests/test_consistency.py -v

# Тесты vector clocks
sudo docker compose exec backend pytest tests/test_vector_clocks.py -v

# API тесты
sudo docker compose exec backend pytest tests/test_api.py -v

# Тесты с покрытием
sudo docker compose exec backend pytest tests/ --cov=app --cov-report=html
```

**Windows:**
```cmd
# Все тесты
docker compose exec backend pytest tests/ -v

# Тесты согласованности
docker compose exec backend pytest tests/test_consistency.py -v

# Тесты vector clocks
docker compose exec backend pytest tests/test_vector_clocks.py -v

# API тесты
docker compose exec backend pytest tests/test_api.py -v

# Тесты с покрытием
docker compose exec backend pytest tests/ --cov=app --cov-report=html
```

### Типы тестов

1. **Unit тесты** - тестирование отдельных компонентов
2. **Integration тесты** - тестирование взаимодействия компонентов
3. **Consistency тесты** - проверка согласованности данных
4. **Vector Clock тесты** - тестирование временных меток
5. **API тесты** - тестирование REST API endpoints

### Сценарии тестирования

- Создание и управление сессиями
- Переключение между репликами
- Обнаружение и разрешение конфликтов
- Vector clock операции
- Concurrent модификации
- Fault tolerance
- Load balancing

## Мониторинг и метрики

- Время отклика API
- Количество активных сессий
- Статус реплик БД
- Частота конфликтов
- Производительность операций чтения/записи
- Vector clock статистика
- События системы

## Устранение неполадок

Подробные инструкции по устранению неполадок см. в файле [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

### Быстрые решения

**Проблема с правами Docker:**
```bash
sudo usermod -aG docker $USER
newgrp docker
```

**Проблема с портами:**
```bash
sudo netstat -tlnp | grep :80
sudo kill -9 <PID>
```

**Очистка системы:**
```bash
sudo docker system prune -a
sudo docker volume prune
```
