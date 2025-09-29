# SQL Dataset Generator - Веб-платформа

Веб-приложение для автоматизации процесса создания, разметки и аугментации обучающих датасетов для дообучения больших языковых моделей. Платформа построена на микросервисной архитектуре с использованием Docker, PostgreSQL, RabbitMQ и React.js.

## 🏗️ Архитектура решения

### Схема архитектуры

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                ВЕБ-ПРИЛОЖЕНИЕ                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐            │
│  │   Frontend      │    │  Admin Dashboard│    │   Load Balancer │            │
│  │   (React.js)    │    │   (React.js)    │    │     (Nginx)     │            │
│  │   Port: 3000    │    │   Port: 3001    │    │    Port: 80     │            │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘            │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              МИКРОСЕРВИСЫ (API)                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐            │
│  │  User Service   │    │  Task Service   │    │ Result Service  │            │
│  │  (FastAPI)      │    │  (FastAPI)      │    │  (FastAPI)      │            │
│  │  Port: 8001     │    │  Port: 8002     │    │  Port: 8003     │            │
│  │  - Auth         │    │  - File Upload  │    │  - Results      │            │
│  │  - Users        │    │  - Processing   │    │  - Download     │            │
│  │  - JWT          │    │  - Parsing      │    │  - Status       │            │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘            │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            ИНФРАСТРУКТУРА                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐            │
│  │   PostgreSQL    │    │    RabbitMQ     │    │   File Storage  │            │
│  │   Port: 5432    │    │  Port: 5672     │    │   /uploads      │            │
│  │  - Users DB     │    │  - Task Events  │    │   /results      │            │
│  │  - Tasks DB     │    │  - User Events  │    │                 │            │
│  │  - Results DB   │    │  - Result Events│    │                 │            │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘            │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Компоненты системы

#### Микросервисы (Backend)
- **User Service** (порт 8001) - управление пользователями, аутентификация и авторизация
- **Task Service** (порт 8002) - обработка файлов, парсинг и аугментация данных
- **Result Service** (порт 8003) - управление результатами обработки

#### Frontend
- **Основное приложение** (порт 3000) - интерфейс для разметчиков
- **Админский дашборд** (порт 3001) - панель администратора с метриками

#### Инфраструктура
- **PostgreSQL** (порт 5432) - основная база данных
- **RabbitMQ** (порты 5672, 15672) - брокер сообщений для межсервисного взаимодействия

## 🛠️ Технологический стек

### Backend
- **Python 3.9+** - основной язык программирования
- **FastAPI** - веб-фреймворк для создания API
- **SQLAlchemy** - ORM для работы с базой данных
- **PostgreSQL** - реляционная база данных
- **RabbitMQ** - брокер сообщений
- **Pandas** - обработка данных
- **OpenPyXL** - работа с Excel файлами
- **JWT** - аутентификация и авторизация

### Frontend
- **React.js 18** - библиотека для создания пользовательских интерфейсов
- **React Router** - маршрутизация
- **Axios** - HTTP клиент
- **React Dropzone** - загрузка файлов
- **Recharts** - графики и диаграммы
- **React Toastify** - уведомления

### DevOps & Infrastructure
- **Docker** - контейнеризация
- **Docker Compose** - оркестрация контейнеров
- **Nginx** - веб-сервер и балансировщик нагрузки
- **Ubuntu 20.04** - операционная система

### Development Tools
- **Git** - система контроля версий
- **VS Code** - редактор кода
- **Postman** - тестирование API

## 🚀 Пошаговая инструкция запуска в Ubuntu 20.04

### Предварительные требования

#### 1. Обновление системы
```bash
sudo apt update && sudo apt upgrade -y
```

#### 2. Установка Docker
```bash
# Удаление старых версий Docker
sudo apt remove docker docker-engine docker.io containerd runc

# Установка зависимостей
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Добавление официального GPG ключа Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Добавление репозитория Docker
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Установка Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER

# Проверка установки
docker --version
```

#### 3. Установка Docker Compose
```bash
# Скачивание Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker compose

# Установка прав на выполнение
sudo chmod +x /usr/local/bin/docker compose

# Проверка установки
docker compose --version
```

#### 4. Установка Git
```bash
sudo apt install -y git
```

### Установка и запуск проекта

#### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd sql-dataset-generator
```

#### 2. Создание необходимых директорий
```bash
mkdir -p uploads results
chmod 755 uploads results
```

#### 3. Настройка переменных окружения (опционально)
```bash
# Копирование примера конфигурации
cp env.example .env

# Редактирование конфигурации
nano .env
```

#### 4. Запуск всех сервисов
```bash
# Запуск в фоновом режиме
docker compose up -d

# Или запуск с выводом логов
docker compose up
```

#### 5. Проверка статуса сервисов
```bash
# Проверка статуса контейнеров
docker compose ps

# Просмотр логов
docker compose logs -f

# Проверка конкретного сервиса
docker compose logs -f user-service
```

#### 6. Проверка работоспособности
```bash
# Проверка доступности API
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health

# Проверка веб-интерфейса
curl http://localhost:3000
curl http://localhost:3001
```

### Автоматический запуск

#### Использование скрипта запуска
```bash
# Сделать скрипт исполняемым
chmod +x start.sh

# Запустить проект
./start.sh
```

#### Настройка автозапуска при загрузке системы
```bash
# Создание systemd сервиса
sudo nano /etc/systemd/system/sql-dataset-generator.service
```

Содержимое файла:
```ini
[Unit]
Description=SQL Dataset Generator
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/sql-dataset-generator
ExecStart=/usr/local/bin/docker compose up -d
ExecStop=/usr/local/bin/docker compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Активация сервиса:
```bash
sudo systemctl enable sql-dataset-generator.service
sudo systemctl start sql-dataset-generator.service
```

### Доступ к приложению

После успешного запуска сервисы будут доступны по следующим адресам:

- **Основное приложение**: http://localhost:3000
- **Админский дашборд**: http://localhost:3001
- **RabbitMQ Management**: http://localhost:15672 (admin/admin)
- **API документация**:
  - User Service: http://localhost:8001/docs
  - Task Service: http://localhost:8002/docs
  - Result Service: http://localhost:8003/docs

### Первый запуск

#### 1. Создание администратора
```bash
# Вход в контейнер user-service
docker compose exec user-service python -c "
from database import SessionLocal
from models import User
from auth import get_password_hash

db = SessionLocal()
admin_user = User(
    username='admin',
    email='admin@example.com',
    hashed_password=get_password_hash('admin123'),
    role='admin'
)
db.add(admin_user)
db.commit()
print('Admin user created successfully')
"
```

#### 2. Проверка работоспособности
```bash
# Проверка всех сервисов
curl -X GET http://localhost:8001/health
curl -X GET http://localhost:8002/health
curl -X GET http://localhost:8003/health

# Проверка веб-интерфейса
curl -I http://localhost:3000
curl -I http://localhost:3001
```

#### 3. Тестирование загрузки файла
```bash
# Создание тестового файла
echo "id,domain,sql_complexity,sql_prompt,sql,sql_explanation
1,test,Beginner,Test query,SELECT 1,Test explanation" > test.csv

# Загрузка через API (требует аутентификации)
curl -X POST http://localhost:8002/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test.csv" \
  -F "target_level=Beginner"
```

## 📋 Использование

### Для разметчиков

1. **Регистрация и вход**
   - Перейдите на http://localhost:3000
   - Зарегистрируйтесь или войдите в систему

2. **Загрузка файла**
   - На вкладке "Загрузить файл" выберите файл .xlsx или .csv
   - Настройте параметры обработки:
     - Целевой уровень сложности (Beginner, Intermediate, Advanced, Expert)
     - Включение аугментации и коэффициент увеличения
   - Нажмите "Загрузить"

3. **Отслеживание прогресса**
   - На вкладке "Мои задачи" отслеживайте статус обработки
   - Статусы: Ожидает → Обрабатывается → Завершено/Ошибка

4. **Скачивание результатов**
   - На вкладке "Результаты" скачайте готовые .jsonl файлы
   - Файлы содержат структурированные данные для обучения LLM

### Для администраторов

1. **Вход в админ-панель**
   - Перейдите на http://localhost:3001
   - Войдите с правами администратора

2. **Мониторинг системы**
   - Просматривайте метрики в реальном времени
   - Отслеживайте активность пользователей
   - Мониторьте статус задач и производительность

## 📁 Формат входных файлов

Поддерживаемые форматы: `.xlsx`, `.csv`

### Обязательные колонки:
- `id` - уникальный идентификатор записи
- `domain` - домен задачи
- `sql_complexity` - уровень сложности (Beginner, Intermediate, Advanced, Expert)
- `sql_prompt` - описание задачи на естественном языке
- `sql` - SQL запрос
- `sql_explanation` - объяснение SQL запроса
- `sql_context` - контекст (схема БД)

### Дополнительные колонки:
- `domain_description` - описание домена
- `sql_complexity_description` - описание сложности
- `sql_task_type` - тип задачи SQL
- `sql_task_type_description` - описание типа задачи

### Колонки для аугментации:
- `prompt_variation_1`, `prompt_variation_2`, ... - вариации описания задачи
- `sql_variation_1`, `sql_variation_2`, ... - вариации SQL запроса

### Пример структуры файла:

| id | domain | sql_complexity | sql_prompt | sql | sql_explanation | sql_context |
|----|--------|----------------|------------|-----|-----------------|-------------|
| 1 | lab1 | Beginner | Показать всех сотрудников | SELECT * FROM employees; | Простейший запрос на выборку | CREATE TABLE employees(id INT, name VARCHAR(50)); |

## 🔧 Настройка и конфигурация

### Переменные окружения

Основные переменные окружения (устанавливаются в docker compose.yml):

- `DATABASE_URL` - строка подключения к PostgreSQL
- `RABBITMQ_URL` - строка подключения к RabbitMQ
- `SECRET_KEY` - секретный ключ для JWT токенов

### Масштабирование

Для увеличения производительности можно:

1. **Увеличить количество экземпляров сервисов**
```yaml
# В docker compose.yml
task-service:
  deploy:
    replicas: 3
```

2. **Настроить балансировщик нагрузки**
```yaml
# Добавить nginx для балансировки
nginx:
  image: nginx
  ports:
    - "80:80"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
```

## 🐛 Устранение неполадок

### Проблемы с запуском

#### 1. Порты заняты
```bash
# Проверить занятые порты
sudo netstat -tulpn | grep :3000
sudo netstat -tulpn | grep :8001
sudo netstat -tulpn | grep :5432

# Остановить конфликтующие сервисы
sudo systemctl stop apache2  # если установлен
sudo systemctl stop nginx    # если установлен
```

#### 2. Проблемы с Docker
```bash
# Пересобрать образы
docker compose build --no-cache

# Очистить неиспользуемые ресурсы
docker system prune -a

# Перезапуск Docker
sudo systemctl restart docker
```

#### 3. Проблемы с базой данных
```bash
# Проверить логи PostgreSQL
docker compose logs postgres

# Пересоздать базу данных
docker compose down -v
docker compose up -d

# Проверить подключение к БД
docker compose exec postgres psql -U postgres -d sql_dataset_generator -c "\dt"
```

#### 4. Проблемы с правами доступа
```bash
# Исправить права на директории
sudo chown -R $USER:$USER uploads results
chmod -R 755 uploads results

# Добавить пользователя в группу docker
sudo usermod -aG docker $USER
# Перелогиниться или выполнить:
newgrp docker
```

#### 5. Проблемы с памятью
```bash
# Проверить использование памяти
free -h
docker stats

# Очистить кэш Docker
docker system prune -a --volumes
```

### Проблемы с обработкой файлов

1. **Файл не загружается**
   - Проверьте формат файла (.xlsx или .csv)
   - Убедитесь, что файл содержит обязательные колонки
   - Проверьте размер файла (рекомендуется до 100MB)

2. **Ошибки парсинга**
   - Проверьте корректность данных в файле
   - Убедитесь, что колонка `id` содержит уникальные числовые значения
   - Проверьте кодировку файла (рекомендуется UTF-8)

## 📊 Мониторинг и логи

### Просмотр логов

```bash
# Все сервисы
docker compose logs -f

# Конкретный сервис
docker compose logs -f task-service
docker compose logs -f user-service
docker compose logs -f result-service

# Логи с временными метками
docker compose logs -f -t

# Последние 100 строк логов
docker compose logs --tail=100 -f
```

### Метрики производительности

- **Админский дашборд**: http://localhost:3001
- **RabbitMQ Management**: http://localhost:15672
- **Логи приложения**: доступны через `docker compose logs`

### Мониторинг системы

```bash
# Статистика контейнеров
docker stats

# Использование дискового пространства
docker system df

# Проверка здоровья контейнеров
docker compose ps
```

### Настройка логирования

```bash
# Создание директории для логов
mkdir -p logs

# Настройка ротации логов в docker compose.yml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## 🔒 Безопасность

### Рекомендации для продакшена

#### 1. Изменить пароли по умолчанию
```yaml
# В docker compose.yml
postgres:
  environment:
    POSTGRES_PASSWORD: your-secure-password

rabbitmq:
  environment:
    RABBITMQ_DEFAULT_PASS: your-secure-password
```

#### 2. Настроить HTTPS
```yaml
# Добавить SSL сертификаты
nginx:
  volumes:
    - ./ssl:/etc/nginx/ssl
```

#### 3. Ограничить доступ к админ-панели
```bash
# Настроить firewall
sudo ufw allow from 192.168.1.0/24 to any port 3001
sudo ufw deny 3001
```

#### 4. Настройка безопасности в Ubuntu
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Настройка firewall
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443

# Отключение неиспользуемых сервисов
sudo systemctl disable apache2
sudo systemctl stop apache2
```

#### 5. Настройка SSL сертификатов
```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx

# Получение SSL сертификата
sudo certbot --nginx -d yourdomain.com
```

## 🤝 Разработка

### Структура проекта

```
sql-dataset-generator/
├── docker compose.yml          # Конфигурация Docker Compose
├── services/                   # Микросервисы
│   ├── user-service/          # Сервис пользователей
│   ├── task-service/          # Сервис задач
│   └── result-service/        # Сервис результатов
├── frontend/                  # Основное приложение
├── admin-dashboard/           # Админский дашборд
├── uploads/                   # Загруженные файлы
├── results/                   # Результаты обработки
└── README.md                  # Документация
```

### Добавление новых функций

1. **Новый микросервис**
```bash
# Создать директорию сервиса
mkdir services/new-service
# Добавить Dockerfile, requirements.txt, main.py
# Обновить docker compose.yml
```

2. **Новые API endpoints**
```python
# В main.py сервиса
@app.post("/new-endpoint")
async def new_endpoint():
    return {"message": "New functionality"}
```

## 📞 Поддержка

### При возникновении проблем:

1. **Проверьте логи сервисов**
```bash
docker compose logs -f
```

2. **Убедитесь, что все сервисы запущены**
```bash
docker compose ps
```

3. **Проверьте конфигурацию docker compose.yml**
```bash
docker compose config
```

4. **Обратитесь к документации API**
- User Service: http://localhost:8001/docs
- Task Service: http://localhost:8002/docs
- Result Service: http://localhost:8003/docs

### Полезные команды для диагностики

```bash
# Проверка состояния всех контейнеров
docker compose ps

# Проверка использования ресурсов
docker stats

# Проверка сетевых подключений
docker network ls
docker network inspect sql-dataset-generator_app-network

# Проверка томов
docker volume ls
```

### Контакты

- **Проект**: SQL Dataset Generator LLM
- **Версия**: 1.0.0
- **Дата**: 2024
- **Разработчик**: ИЦО МГПУ
- **Курсовая работа**: "Проектирование распределенной платформы для краудсорсинговой разметки пар 'естественный язык - SQL'"

## 📄 Лицензия

Проект разработан для образовательных целей МГПУ в рамках курсовой работы по дисциплине "Распределенные системы".

---

**Версия**: 1.0.0  
**Дата**: 2024  
**Разработчик**: ИЦО МГПУ  
**ОС**: Ubuntu 20.04 LTS

