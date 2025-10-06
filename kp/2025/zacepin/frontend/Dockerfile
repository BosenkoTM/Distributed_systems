FROM node:18-alpine

WORKDIR /app

# Копирование package.json и package-lock.json
COPY package*.json ./

# Установка зависимостей
RUN npm ci --only=production

# Копирование исходного кода
COPY . .

# Открытие порта
EXPOSE 3000

# Команда запуска
CMD ["npm", "start"]
