# Устранение неполадок

## Общие проблемы

### 1. Ошибка "Permission denied" при запуске Docker

**Проблема:** Пользователь не добавлен в группу docker

**Решение:**
```bash
# Добавить пользователя в группу docker
sudo usermod -aG docker $USER

# Перелогиниться или выполнить:
newgrp docker

# Проверить группу
groups $USER
```

### 2. Ошибка "docker compose: command not found"

**Проблема:** Docker Compose V2 не установлен

**Решение для Ubuntu:**
```bash
# Установка Docker Compose V2
sudo apt update
sudo apt install docker-compose-plugin

# Проверка установки
docker compose version
```

### 3. Ошибка "Port already in use"

**Проблема:** Порт занят другим процессом

**Решение:**
```bash
# Найти процесс, использующий порт
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :3000
sudo netstat -tlnp | grep :8000

# Остановить процесс
sudo kill -9 <PID>

# Или изменить порты в docker-compose.yml
```

### 4. Ошибка "No space left on device"

**Проблема:** Недостаточно места на диске

**Решение:**
```bash
# Проверить использование диска
df -h

# Очистить неиспользуемые Docker ресурсы
sudo docker system prune -a
sudo docker volume prune
sudo docker image prune -a

# Удалить старые логи
sudo journalctl --vacuum-time=7d
```

### 5. Ошибка "Connection refused" к базе данных

**Проблема:** PostgreSQL не запустился или недоступен

**Решение:**
```bash
# Проверить статус контейнеров
sudo docker compose ps

# Проверить логи PostgreSQL
sudo docker compose logs postgres-master

# Перезапустить базу данных
sudo docker compose restart postgres-master
```

## Проблемы с репликацией

### 1. Реплики не синхронизируются

**Проблема:** Проблемы с настройкой репликации

**Решение:**
```bash
# Проверить статус реплик
sudo docker compose logs postgres-replica-1
sudo docker compose logs postgres-replica-2

# Пересоздать реплики
sudo docker compose down
sudo docker volume rm zacepin_postgres_replica1_data
sudo docker volume rm zacepin_postgres_replica2_data
sudo docker compose up -d
```

### 2. Ошибка "replication slot does not exist"

**Проблема:** Слот репликации не создан

**Решение:**
```bash
# Подключиться к master базе
sudo docker compose exec postgres-master psql -U postgres -d labeling_db

# Создать слот репликации
SELECT pg_create_physical_replication_slot('replica1_slot');
SELECT pg_create_physical_replication_slot('replica2_slot');
```

## Проблемы с приложением

### 1. Frontend не загружается

**Проблема:** Проблемы с React приложением

**Решение:**
```bash
# Проверить логи frontend
sudo docker compose logs frontend

# Пересобрать frontend
sudo docker compose build frontend
sudo docker compose up -d frontend
```

### 2. Backend API не отвечает

**Проблема:** Проблемы с FastAPI приложением

**Решение:**
```bash
# Проверить логи backend
sudo docker compose logs backend

# Проверить подключение к базе данных
sudo docker compose exec backend python -c "from app.core.database import db_manager; print(db_manager.replica_health)"

# Перезапустить backend
sudo docker compose restart backend
```

### 3. Ошибки с vector clocks

**Проблема:** Проблемы с синхронизацией временных меток

**Решение:**
```bash
# Очистить кэш vector clocks
sudo docker compose exec redis redis-cli FLUSHDB

# Перезапустить backend
sudo docker compose restart backend
```

## Проблемы с производительностью

### 1. Медленная работа системы

**Проблема:** Недостаточно ресурсов

**Решение:**
```bash
# Проверить использование ресурсов
sudo docker stats

# Увеличить лимиты в docker-compose.yml
# Добавить в секции services:
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '1.0'
```

### 2. Высокое использование памяти

**Проблема:** Утечки памяти

**Решение:**
```bash
# Проверить использование памяти
free -h
sudo docker stats

# Ограничить память для контейнеров
sudo docker update --memory=1g <container_name>
```

## Проблемы с сетью

### 1. Контейнеры не могут связаться друг с другом

**Проблема:** Проблемы с Docker сетью

**Решение:**
```bash
# Проверить сеть
sudo docker network ls
sudo docker network inspect zacepin_labeling_network

# Пересоздать сеть
sudo docker compose down
sudo docker network prune
sudo docker compose up -d
```

### 2. Nginx не проксирует запросы

**Проблема:** Проблемы с конфигурацией Nginx

**Решение:**
```bash
# Проверить конфигурацию Nginx
sudo docker compose exec nginx nginx -t

# Перезапустить Nginx
sudo docker compose restart nginx

# Проверить логи
sudo docker compose logs nginx
```

## Проблемы с тестами

### 1. Тесты не проходят

**Проблема:** Проблемы с тестовой средой

**Решение:**
```bash
# Запустить тесты с подробным выводом
sudo docker compose exec backend pytest tests/ -v -s

# Запустить конкретный тест
sudo docker compose exec backend pytest tests/test_consistency.py::TestConsistency::test_vector_clock_ordering -v

# Проверить покрытие
sudo docker compose exec backend pytest tests/ --cov=app --cov-report=term-missing
```

### 2. Ошибки с тестовой базой данных

**Проблема:** Проблемы с SQLite в тестах

**Решение:**
```bash
# Очистить тестовую базу данных
sudo docker compose exec backend rm -f test.db

# Запустить тесты заново
sudo docker compose exec backend pytest tests/ -v
```

## Логи и диагностика

### Просмотр логов
```bash
# Все логи
sudo docker compose logs -f

# Логи конкретного сервиса
sudo docker compose logs -f backend
sudo docker compose logs -f frontend
sudo docker compose logs -f postgres-master

# Логи за последние 100 строк
sudo docker compose logs --tail=100 backend
```

### Диагностика системы
```bash
# Статус контейнеров
sudo docker compose ps

# Использование ресурсов
sudo docker stats

# Информация о системе
sudo docker system df
sudo docker system info
```

### Очистка системы
```bash
# Остановка всех контейнеров
sudo docker compose down

# Удаление volumes
sudo docker compose down -v

# Полная очистка
sudo docker system prune -a --volumes
```

## Восстановление после сбоя

### Полная переустановка
```bash
# Остановка и удаление всех контейнеров
sudo docker compose down -v --rmi all

# Очистка volumes
sudo docker volume prune -f

# Пересборка и запуск
sudo docker compose up --build -d

# Инициализация базы данных
sudo docker compose exec backend python init_db.py
```

### Восстановление данных
```bash
# Создание бэкапа
sudo docker compose exec postgres-master pg_dump -U postgres labeling_db > backup.sql

# Восстановление из бэкапа
sudo docker compose exec -T postgres-master psql -U postgres labeling_db < backup.sql
```

## Контакты и поддержка

Если проблемы не решаются:

1. Проверьте логи всех сервисов
2. Убедитесь, что все требования выполнены
3. Попробуйте полную переустановку
4. Обратитесь к документации Docker и используемых технологий
