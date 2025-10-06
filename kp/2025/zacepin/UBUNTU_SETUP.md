# Установка и настройка на Ubuntu

## Системные требования

- Ubuntu 20.04 LTS или новее
- Минимум 4GB RAM
- 10GB свободного места на диске
- Права sudo

## Установка Docker

### 1. Обновление системы
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Установка зависимостей
```bash
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release
```

### 3. Добавление GPG ключа Docker
```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
```

### 4. Добавление репозитория Docker
```bash
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

### 5. Установка Docker
```bash
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

### 6. Настройка Docker
```bash
# Добавление пользователя в группу docker
sudo usermod -aG docker $USER

# Включение автозапуска Docker
sudo systemctl enable docker
sudo systemctl start docker

# Проверка установки
docker --version
docker compose version
```

### 7. Перезагрузка системы
```bash
sudo reboot
```

## Установка дополнительных инструментов

### Git (если не установлен)
```bash
sudo apt install -y git
```

### Дополнительные утилиты
```bash
sudo apt install -y htop tree wget curl
```

## Запуск проекта

### 1. Клонирование проекта
```bash
git clone <repository-url>
cd zacepin
```

### 2. Настройка прав доступа
```bash
chmod +x start.sh
```

### 3. Запуск системы
```bash
./start.sh
```

## Устранение неполадок

### Проблема с правами Docker
Если возникают проблемы с правами доступа к Docker:
```bash
# Перелогиниться в систему или выполнить:
newgrp docker

# Проверить группу пользователя
groups $USER
```

### Проблема с портами
Если порты заняты:
```bash
# Проверить занятые порты
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :3000
sudo netstat -tlnp | grep :8000

# Остановить процессы на портах
sudo kill -9 <PID>
```

### Проблема с памятью
Если не хватает памяти:
```bash
# Проверить использование памяти
free -h

# Очистить кэш Docker
sudo docker system prune -a
```

### Проблема с дисковым пространством
```bash
# Проверить использование диска
df -h

# Очистить неиспользуемые образы Docker
sudo docker image prune -a
```

## Мониторинг системы

### Проверка статуса контейнеров
```bash
sudo docker compose ps
```

### Просмотр логов
```bash
# Все логи
sudo docker compose logs -f

# Логи конкретного сервиса
sudo docker compose logs -f backend
sudo docker compose logs -f frontend
sudo docker compose logs -f postgres-master
```

### Проверка ресурсов
```bash
# Использование ресурсов контейнерами
sudo docker stats

# Информация о системе
htop
```

## Остановка и очистка

### Остановка системы
```bash
sudo docker compose down
```

### Полная очистка
```bash
# Остановка и удаление контейнеров
sudo docker compose down -v

# Удаление образов
sudo docker compose down --rmi all

# Очистка volumes
sudo docker volume prune
```

## Безопасность

### Настройка файрвола (опционально)
```bash
# Установка UFW
sudo apt install -y ufw

# Разрешение SSH
sudo ufw allow ssh

# Разрешение HTTP/HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Включение файрвола
sudo ufw enable
```

### Регулярные обновления
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Обновление Docker
sudo apt update && sudo apt install --only-upgrade docker-ce docker-ce-cli containerd.io
```

## Производительность

### Оптимизация Docker
```bash
# Настройка лимитов для Docker
sudo systemctl edit docker

# Добавить в файл:
[Service]
ExecStart=
ExecStart=/usr/bin/dockerd --default-ulimit nofile=65536:65536
```

### Мониторинг производительности
```bash
# Установка дополнительных инструментов мониторинга
sudo apt install -y iotop nethogs

# Мониторинг I/O
sudo iotop

# Мониторинг сети
sudo nethogs
```
