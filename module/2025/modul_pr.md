# Практические задания модульного экзамена
## Дисциплина: Распределенные системы
### Бакалавриат, 3 курс, направление "Бизнес-информатика"

---

## Практическое задание №1. Реализация RPC-сервиса с использованием gRPC

### Постановка задачи

Компания "ТехноБанк" разрабатывает распределенную систему управления счетами клиентов. Вам поручено спроектировать и реализовать gRPC-сервис для операций со счетами, который будет взаимодействовать с микросервисами аналитики, нотификаций и аудита.

### Бизнес-требования

Сервис должен поддерживать следующие операции:
1. **Получение баланса счета** (Unary RPC)
2. **Потоковая выгрузка истории транзакций** за период (Server Streaming RPC)
3. **Пакетное зачисление средств** от нескольких источников (Client Streaming RPC)
4. **Мониторинг транзакций в реальном времени** между клиентом и сервером (Bidirectional Streaming RPC)

### Задание

#### Часть 1. Проектирование proto-контракта (30 баллов)

Разработайте файл `banking_service.proto`, который должен включать:

1. **Определение сервиса** `BankingService` с четырьмя методами (по одному каждого типа RPC)

2. **Сообщения запросов:**
   - `GetBalanceRequest` - содержит account_id (string)
   - `TransactionHistoryRequest` - содержит account_id, start_date, end_date
   - `DepositRequest` - содержит account_id, amount (double), source (string)
   - `MonitorRequest` - содержит account_id, filter_type (enum: ALL, INCOMING, OUTGOING)

3. **Сообщения ответов:**
   - `BalanceResponse` - account_id, balance, currency, last_update (timestamp)
   - `Transaction` - transaction_id, amount, type, timestamp, description
   - `DepositSummary` - total_deposited, transaction_count, status
   - `MonitorEvent` - event_type (enum: DEPOSIT, WITHDRAWAL, TRANSFER), transaction

4. **Enum типы:**
   - `TransactionType`: DEPOSIT, WITHDRAWAL, TRANSFER
   - `FilterType`: ALL, INCOMING, OUTGOING
   - `Status`: SUCCESS, PENDING, FAILED

**Требуется:**
- Написать полный proto-файл с комментариями
- Обосновать выбор типов полей
- Объяснить, почему каждая операция реализована определенным типом RPC

#### Часть 2. Реализация серверной части (40 баллов)

Реализуйте класс `BankingServiceServicer` на Python:

```python
import grpc
from concurrent import futures
import banking_service_pb2
import banking_service_pb2_grpc
import time
from datetime import datetime

class BankingServiceServicer(banking_service_pb2_grpc.BankingServiceServicer):
    def __init__(self):
        # Имитация базы данных
        self.accounts = {
            "ACC001": {"balance": 15000.00, "currency": "RUB"},
            "ACC002": {"balance": 5000.00, "currency": "RUB"}
        }
        self.transactions = []  # История транзакций
    
    # TODO: Реализовать методы
    def GetBalance(self, request, context):
        pass
    
    def StreamTransactionHistory(self, request, context):
        pass
    
    def BatchDeposit(self, request_iterator, context):
        pass
    
    def MonitorTransactions(self, request_iterator, context):
        pass
```

**Требуется реализовать:**

1. **GetBalance** (Unary):
   - Проверка существования счета
   - Возврат баланса с текущей датой-временем
   - Обработка ошибки "счет не найден" (gRPC status code NOT_FOUND)

2. **StreamTransactionHistory** (Server Streaming):
   - Генерация потока из 10 транзакций для счета
   - Задержка между сообщениями 0.5 сек (имитация загрузки из БД)
   - Фильтрация по датам start_date и end_date

3. **BatchDeposit** (Client Streaming):
   - Прием потока запросов на зачисление
   - Накопление total_deposited и transaction_count
   - Возврат итоговой сводки после завершения потока

4. **MonitorTransactions** (Bidirectional Streaming):
   - Прием фильтров от клиента
   - Отправка событий транзакций согласно фильтру
   - Обновление фильтра по запросу клиента

#### Часть 3. Реализация клиентской части (20 баллов)

Реализуйте клиент, который:

1. Вызывает GetBalance для счета "ACC001"
2. Подписывается на StreamTransactionHistory для счета "ACC001"
3. Отправляет 5 запросов BatchDeposit
4. Устанавливает bidirectional stream для мониторинга с динамической сменой фильтра

#### Часть 4. Анализ и оптимизация (10 баллов)

**Требуется найти и проанализировать:**

1. **Время отклика (latency):**
   - Замерьте среднее время для каждого типа RPC-вызова
   - Объясните разницу между unary и streaming вызовами

2. **Пропускная способность:**
   - Рассчитайте количество транзакций в секунду для Server Streaming
   - Оцените влияние задержки (0.5 сек) на производительность

3. **Использование ресурсов:**
   - Какой объем данных передается для Bidirectional Streaming за 1 минуту?
   - Предложите оптимизацию для снижения нагрузки

4. **Обработка ошибок:**
   - Продемонстрируйте обработку следующих сценариев:
     - Клиент запрашивает несуществующий счет
     - Обрыв соединения во время streaming
     - Таймаут при долгом выполнении запроса

### Формат сдачи

**Файлы для предоставления:**
1. `banking_service.proto` - proto-контракт с комментариями
2. `server.py` - реализация сервера
3. `client.py` - реализация клиента
4. `analysis.md` - отчет с результатами анализа, графиками latency и обоснованиями

**Критерии оценки:**
- Корректность proto-контракта (30%)
- Реализация всех четырех типов RPC (40%)
- Функциональность клиента (20%)
- Качество анализа и оптимизации (10%)

---

## Практическое задание №2. Проектирование RESTful API с Nginx в качестве обратного прокси

### Постановка задачи

Онлайн-ритейлер "МаркетПлейс" разрабатывает систему управления каталогом товаров. Вам необходимо спроектировать и реализовать RESTful API на Flask, настроить Nginx в качестве обратного прокси-сервера и обеспечить высокую доступность системы.

### Бизнес-требования

API должно поддерживать:
1. **CRUD операции** для товаров (Product)
2. **Фильтрацию** товаров по категориям и ценовому диапазону
3. **Пагинацию** для списка товаров
4. **Полнотекстовый поиск** по названию и описанию
5. **Кэширование** часто запрашиваемых данных

### Задание

#### Часть 1. Проектирование RESTful API (25 баллов)

Разработайте спецификацию API:

**Ресурс: Products**

| HTTP метод | Endpoint | Описание | Request Body | Response |
|------------|----------|----------|--------------|----------|
| GET | /api/products | Список товаров с пагинацией | - | 200 OK + JSON array |
| GET | /api/products/:id | Получить товар по ID | - | 200 OK / 404 Not Found |
| POST | /api/products | Создать новый товар | JSON | 201 Created |
| PUT | /api/products/:id | Обновить товар | JSON | 200 OK / 404 Not Found |
| DELETE | /api/products/:id | Удалить товар | - | 204 No Content |
| GET | /api/products/search?q=...&category=...&min_price=...&max_price=...&page=...&limit=... | Поиск с фильтрами | - | 200 OK |

**Модель Product:**
```json
{
  "id": "string (UUID)",
  "name": "string",
  "description": "string",
  "price": "number",
  "category": "string",
  "stock": "integer",
  "created_at": "ISO 8601 timestamp",
  "updated_at": "ISO 8601 timestamp"
}
```

**Требуется:**
- Описать все endpoints с примерами запросов/ответов
- Определить HTTP коды состояния для каждого сценария (успех, ошибки)
- Спроектировать валидацию входных данных
- Описать формат сообщений об ошибках

#### Часть 2. Реализация Flask API (35 баллов)

Реализуйте `app.py`:

```python
from flask import Flask, jsonify, request
from uuid import uuid4
from datetime import datetime

app = Flask(__name__)

# Имитация БД в памяти
products = []

@app.route('/api/products', methods=['GET'])
def get_products():
    """
    TODO: Реализовать пагинацию
    Параметры: page (default=1), limit (default=10)
    """
    pass

@app.route('/api/products/<product_id>', methods=['GET'])
def get_product(product_id):
    """TODO: Получить товар по ID"""
    pass

@app.route('/api/products', methods=['POST'])
def create_product():
    """
    TODO: Создать товар
    Валидация: name, price, category обязательны
    """
    pass

@app.route('/api/products/<product_id>', methods=['PUT'])
def update_product(product_id):
    """TODO: Обновить товар"""
    pass

@app.route('/api/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    """TODO: Удалить товар"""
    pass

@app.route('/api/products/search', methods=['GET'])
def search_products():
    """
    TODO: Поиск с фильтрами
    Параметры: q, category, min_price, max_price, page, limit
    """
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

**Требуется реализовать:**

1. **Валидация данных:**
   - Проверка обязательных полей
   - Проверка типов (price > 0, stock >= 0)
   - Возврат 400 Bad Request с описанием ошибок

2. **Пагинация:**
   - Параметры query string: `page`, `limit`
   - Метаинформация в ответе: `total`, `page`, `pages`, `items`

3. **Фильтрация и поиск:**
   - Фильтрация по `category`, `min_price`, `max_price`
   - Полнотекстовый поиск по `name` и `description` (параметр `q`)

4. **Обработка ошибок:**
   - 404 Not Found для несуществующих ресурсов
   - 400 Bad Request для невалидных данных
   - 500 Internal Server Error для неожиданных ошибок

#### Часть 3. Настройка Nginx (25 баллов)

Создайте конфигурацию Nginx (`/etc/nginx/sites-available/marketplace`):

**Требования:**

1. **Обратный прокси:**
   - Проксирование всех запросов `/api/*` на Flask (localhost:5000)
   - Передача заголовков: X-Real-IP, X-Forwarded-For, X-Forwarded-Proto

2. **Кэширование:**
   - Кэширование GET-запросов на `/api/products` на 5 минут
   - Кэширование GET-запросов на `/api/products/:id` на 10 минут
   - Отключение кэширования для POST, PUT, DELETE
   - Добавление заголовка `X-Cache-Status: HIT/MISS`

3. **Rate Limiting:**
   - Ограничение: не более 100 запросов в минуту с одного IP
   - Возврат 429 Too Many Requests при превышении лимита

4. **Балансировка нагрузки:**
   - Настроить upstream с двумя Flask-инстансами (порты 5000, 5001)
   - Алгоритм: least_conn

5. **Дополнительно:**
   - Gzip сжатие для JSON-ответов
   - Логирование времени обработки запросов
   - Кастомные заголовки: `X-API-Version: 1.0`

**Пример конфигурации (заполнить недостающее):**

```nginx
# Определение upstream
upstream flask_app {
    least_conn;
    # TODO: добавить серверы
}

# Настройка кэша
proxy_cache_path /var/cache/nginx/api levels=1:2 keys_zone=api_cache:10m max_size=100m inactive=60m;

# Rate limiting
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/m;

server {
    listen 80;
    server_name marketplace.local;

    # Логирование
    access_log /var/log/nginx/marketplace_access.log;
    error_log /var/log/nginx/marketplace_error.log;

    # Gzip compression
    # TODO: настроить gzip

    location /api/ {
        # Rate limiting
        # TODO: применить rate limiting

        # Проксирование
        # TODO: настроить proxy_pass

        # Кэширование
        # TODO: настроить proxy_cache

        # Заголовки
        # TODO: добавить заголовки
    }
}
```

#### Часть 4. Тестирование и анализ производительности (15 баллов)

**Требуется найти и проанализировать:**

1. **HTTP-анализ с curl:**
   ```bash
   # Создание товара
   curl -X POST http://localhost/api/products \
     -H "Content-Type: application/json" \
     -d '{"name":"Laptop","description":"Gaming laptop","price":75000,"category":"Electronics","stock":10}'
   
   # Получение списка с пагинацией
   curl "http://localhost/api/products?page=1&limit=5"
   
   # Поиск с фильтрами
   curl "http://localhost/api/products/search?category=Electronics&min_price=50000&max_price=100000"
   ```
   
   Проанализируйте:
   - Заголовки ответа (X-Cache-Status, X-API-Version)
   - Время отклика (используйте `curl -w "@curl-format.txt"`)
   - Размер ответа до и после gzip

2. **Тестирование кэширования:**
   - Выполните GET-запрос дважды
   - Сравните заголовок `X-Cache-Status: MISS` vs `HIT`
   - Измерьте разницу во времени отклика

3. **Тестирование Rate Limiting:**
   - Используйте скрипт для отправки 150 запросов
   - Подсчитайте количество ответов 429
   - Проверьте заголовок `Retry-After`

4. **Нагрузочное тестирование:**
   - Используйте Apache Bench: `ab -n 1000 -c 10 http://localhost/api/products`
   - Зафиксируйте:
     - Requests per second
     - Time per request (mean)
     - Процент успешных запросов

5. **Балансировка нагрузки:**
   - Запустите 2 Flask-инстанса
   - Проверьте логи Nginx: распределяются ли запросы между серверами
   - Остановите один инстанс: продолжает ли работать API?

### Формат сдачи

**Файлы для предоставления:**
1. `api_specification.md` - описание endpoints с примерами
2. `app.py` - полная реализация Flask API
3. `marketplace.conf` - конфигурация Nginx
4. `testing_report.md` - отчет с результатами тестирования (curl команды, скриншоты, графики производительности)

**Критерии оценки:**
- Корректность проектирования API (25%)
- Полнота реализации Flask endpoints (35%)
- Правильность настройки Nginx (25%)
- Качество тестирования и анализа (15%)

---

## Практическое задание №3. Асинхронное взаимодействие через RabbitMQ и gRPC

### Постановка задачи

Компания "ЛогистикПро" разрабатывает систему отслеживания доставки посылок. Система состоит из трех микросервисов:
1. **Order Service** - прием заказов на доставку
2. **Routing Service** - расчет маршрута (gRPC)
3. **Notification Service** - отправка уведомлений клиентам

Вам необходимо реализовать асинхронное взаимодействие через брокер RabbitMQ и синхронные вызовы через gRPC.

### Бизнес-требования

При создании заказа на доставку:
1. Order Service публикует сообщение в RabbitMQ (очередь `orders`)
2. Routing Service (Consumer) обрабатывает заказ:
   - Вызывает gRPC-сервис для расчета маршрута
   - Публикует результат в очередь `routes`
3. Notification Service (Consumer) отправляет уведомление клиенту

### Задание

#### Часть 1. Проектирование архитектуры (20 баллов)

**Требуется разработать:**

1. **Диаграмму взаимодействия компонентов:**
   - Покажите потоки данных между сервисами
   - Укажите типы взаимодействия (асинхронное через RabbitMQ, синхронное через gRPC)
   - Опишите структуру сообщений в очередях

2. **Топологию RabbitMQ:**
   - Exchange: `logistics_exchange` (тип: direct)
   - Очереди: `orders`, `routes`, `notifications`
   - Routing keys: `order.created`, `route.calculated`, `notification.send`

3. **gRPC контракт (`routing_service.proto`):**
   ```protobuf
   syntax = "proto3";
   
   package routing;
   
   service RoutingService {
       // Расчет маршрута
       rpc CalculateRoute(RouteRequest) returns (RouteResponse) {}
   }
   
   message RouteRequest {
       string order_id = 1;
       string origin = 2;        // Адрес отправления
       string destination = 3;   // Адрес назначения
       double weight = 4;        // Вес посылки (кг)
   }
   
   message RouteResponse {
       string order_id = 1;
       string route_id = 2;
       int32 distance = 3;       // Расстояние (км)
       int32 estimated_time = 4; // Время доставки (часы)
       double cost = 5;          // Стоимость доставки
   }
   ```

4. **Структура сообщений в RabbitMQ (JSON):**
   ```json
   // Сообщение в очередь orders
   {
     "order_id": "ORD-12345",
     "customer_id": "CUST-001",
     "customer_email": "customer@example.com",
     "origin": "Москва, ул. Ленина, 1",
     "destination": "Санкт-Петербург, Невский пр., 10",
     "weight": 5.5,
     "created_at": "2025-12-01T10:00:00Z"
   }
   
   // Сообщение в очередь routes
   {
     "order_id": "ORD-12345",
     "route_id": "ROUTE-7890",
     "distance": 700,
     "estimated_time": 12,
     "cost": 1500.00,
     "calculated_at": "2025-12-01T10:00:05Z"
   }
   
   // Сообщение в очередь notifications
   {
     "order_id": "ORD-12345",
     "customer_email": "customer@example.com",
     "subject": "Ваш заказ обработан",
     "message": "Маршрут рассчитан. Ожидаемое время доставки: 12 часов. Стоимость: 1500 руб."
   }
   ```

#### Часть 2. Реализация микросервисов (50 баллов)

**A. Order Service (Producer)**

```python
import pika
import json
from uuid import uuid4
from datetime import datetime

class OrderService:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='localhost',
                credentials=pika.PlainCredentials('user', 'password')
            )
        )
        self.channel = self.connection.channel()
        
        # TODO: Объявить exchange и очередь orders
        
    def create_order(self, customer_id, customer_email, origin, destination, weight):
        """
        TODO: Создать заказ и опубликовать в RabbitMQ
        1. Сгенерировать order_id
        2. Создать JSON сообщение
        3. Опубликовать с routing_key='order.created'
        4. Вернуть order_id
        """
        pass
    
    def close(self):
        self.connection.close()

# Пример использования
if __name__ == '__main__':
    service = OrderService()
    order_id = service.create_order(
        customer_id="CUST-001",
        customer_email="customer@example.com",
        origin="Москва, ул. Ленина, 1",
        destination="Санкт-Петербург, Невский пр., 10",
        weight=5.5
    )
    print(f"Заказ создан: {order_id}")
    service.close()
```

**B. Routing Service (Consumer + gRPC Server)**

```python
import pika
import json
import grpc
from concurrent import futures
import routing_service_pb2
import routing_service_pb2_grpc
import random

# gRPC Server
class RoutingServiceServicer(routing_service_pb2_grpc.RoutingServiceServicer):
    def CalculateRoute(self, request, context):
        """
        TODO: Реализовать расчет маршрута
        1. Имитировать расчет расстояния (случайное 500-1000 км)
        2. Рассчитать время: distance / 60 (км/ч)
        3. Рассчитать стоимость: distance * 2 (руб/км)
        4. Вернуть RouteResponse
        """
        pass

def serve_grpc():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    routing_service_pb2_grpc.add_RoutingServiceServicer_to_server(
        RoutingServiceServicer(), server
    )
    server.add_insecure_port('[::]:50051')
    print("gRPC сервер запущен на порту 50051")
    server.start()
    server.wait_for_termination()

# RabbitMQ Consumer
class RoutingConsumer:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='localhost',
                credentials=pika.PlainCredentials('user', 'password')
            )
        )
        self.channel = self.connection.channel()
        
        # TODO: Объявить exchange и очереди
        
        # gRPC клиент для вызова RoutingService
        self.grpc_channel = grpc.insecure_channel('localhost:50051')
        self.grpc_stub = routing_service_pb2_grpc.RoutingServiceStub(self.grpc_channel)
    
    def callback(self, ch, method, properties, body):
        """
        TODO: Обработать сообщение из очереди orders
        1. Распарсить JSON
        2. Вызвать gRPC CalculateRoute
        3. Опубликовать результат в очередь routes с routing_key='route.calculated'
        4. Подтвердить обработку (ack)
        """
        pass
    
    def start_consuming(self):
        self.channel.basic_consume(queue='orders', on_message_callback=self.callback)
        print("Ожидание заказов...")
        self.channel.start_consuming()

if __name__ == '__main__':
    # Запустить gRPC сервер в отдельном потоке
    import threading
    grpc_thread = threading.Thread(target=serve_grpc, daemon=True)
    grpc_thread.start()
    
    # Запустить RabbitMQ Consumer
    consumer = RoutingConsumer()
    consumer.start_consuming()
```

**C. Notification Service (Consumer)**

```python
import pika
import json

class NotificationService:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='localhost',
                credentials=pika.PlainCredentials('user', 'password')
            )
        )
        self.channel = self.connection.channel()
        
        # TODO: Объявить exchange и очередь notifications
    
    def callback(self, ch, method, properties, body):
        """
        TODO: Обработать сообщение из очереди notifications
        1. Распарсить JSON
        2. Имитировать отправку email (print в консоль)
        3. Подтвердить обработку (ack)
        """
        pass
    
    def start_consuming(self):
        self.channel.basic_consume(queue='notifications', on_message_callback=self.callback)
        print("Ожидание уведомлений...")
        self.channel.start_consuming()

if __name__ == '__main__':
    service = NotificationService()
    service.start_consuming()
```

#### Часть 3. Docker Compose для RabbitMQ (10 баллов)

Создайте `docker-compose.yml`:

```yaml
version: '3.8'

services:
  rabbitmq:
    image: rabbitmq:3.13-management
    container_name: rabbitmq_logistics
    ports:
      - "5672:5672"    # AMQP
      - "15672:15672"  # Management UI
    environment:
      RABBITMQ_DEFAULT_USER: user
      RABBITMQ_DEFAULT_PASS: password
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    healthcheck:
      test: ["CMD", "rabbitmqctl", "status"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  rabbitmq_data:
```

#### Часть 4. Тестирование и анализ (20 баллов)

**Требуется найти и проанализировать:**

1. **Время обработки сообщений:**
   - Создайте 10 заказов через Order Service
   - Измерьте время от публикации в `orders` до получения в `notifications`
   - Постройте график "Order ID vs Processing Time"

2. **Пропускная способность системы:**
   - Отправьте 100 заказов
   - Рассчитайте среднее количество обработанных заказов в секунду
   - Формула: `throughput = total_orders / total_time`

3. **Надежность доставки:**
   - Продемонстрируйте, что происходит, если:
     - Routing Service отключен (сообщения накапливаются в очереди)
     - gRPC сервер недоступен (обработка сообщения повторяется)
   - Объясните роль `basic_ack` в обеспечении at-least-once delivery

4. **Сравнение с синхронной архитектурой:**
   - Оцените, сколько времени заняла бы обработка при синхронных HTTP-вызовах
   - Преимущества асинхронной архитектуры:
     - Temporal decoupling
     - Buffering в очереди
     - Возможность масштабирования Consumer'ов

5. **Мониторинг через RabbitMQ Management UI:**
   - Откройте http://localhost:15672
   - Зафиксируйте (скриншоты):
     - Количество сообщений в очередях
     - Message rates (incoming/outgoing)
     - Количество Consumer'ов на каждой очереди

### Формат сдачи

**Файлы для предоставления:**
1. `architecture.md` - описание архитектуры, диаграммы
2. `routing_service.proto` - proto-контракт
3. `order_service.py` - Producer
4. `routing_service.py` - Consumer + gRPC Server
5. `notification_service.py` - Consumer
6. `docker-compose.yml` - конфигурация RabbitMQ
7. `performance_analysis.md` - результаты тестирования с графиками и выводами

**Критерии оценки:**
- Корректность архитектуры и проектирования (20%)
- Реализация Order Service (15%)
- Реализация Routing Service (25%)
- Реализация Notification Service (10%)
- Docker Compose конфигурация (10%)
- Качество анализа производительности (20%)

---

## Практическое задание №4. Обнаружение отказов и надежность распределенной системы

### Постановка задачи

Вы - архитектор распределенной системы "CloudMonitor" для мониторинга серверов в дата-центре. Система состоит из N узлов, которые должны обнаруживать отказы друг друга и обеспечивать высокую доступность. Необходимо спроектировать и проанализировать протокол обнаружения отказов, оптимизировав параметры для баланса между скоростью обнаружения и использованием сетевых ресурсов.

### Бизнес-требования

1. **Обнаружение отказов:** Система должна обнаруживать выход узла из строя не позднее чем через 5 секунд
2. **Масштабируемость:** Поддержка до 100 узлов в кластере
3. **Эффективность:** Минимальное использование полосы пропускания (< 10 Кбит/с на узел)
4. **Устойчивость к сетевым проблемам:** Корректная работа при потере до 10% пакетов
5. **Отказоустойчивость:** Система продолжает работать при отказе до 20% узлов

### Задание

#### Часть 1. Теоретический анализ протоколов (25 баллов)

**Требуется проанализировать:**

1. **Сравнение протоколов обнаружения отказов:**

   | Характеристика | Heartbeat (централизованный) | Heartbeat (peer-to-peer) | Gossip (Serf) |
   |----------------|------------------------------|-------------------------|----------------|
   | Время обнаружения первого отказа | ? | ? | ? |
   | Время полной конвергенции | ? | ? | ? |
   | Использование полосы пропускания | O(?) | O(?) | O(?) |
   | Масштабируемость | ? | ? | ? |
   | Single point of failure | ? | ? | ? |
   | Устойчивость к сетевым разделениям | ? | ? | ? |

2. **Модель протокола Gossip:**
   - Объясните алгоритм распространения информации об отказе
   - Опишите влияние параметров:
     - Gossip Interval (τ) - интервал между раундами
     - Gossip Fanout (k) - количество узлов для контакта
   - Математическая модель времени конвергенции:
     ```
     T_convergence ≈ τ × log_k(N)
     где N - количество узлов
     ```

3. **Проблема ложных срабатываний (false positives):**
   - Объясните причины (сетевые задержки, перегрузка узла)
   - Методы снижения: timeout tuning, adaptive timeouts
   - Trade-off между скоростью обнаружения и точностью

#### Часть 2. Симуляция с Serf Convergence Simulator (35 баллов)

Используйте симулятор: https://www.serf.io/docs/internals/simulator.html

**Эксперимент 1: Влияние Gossip Interval**

Зафиксируйте параметры:
- Nodes: 50
- Gossip Fanout: 3
- Packet Loss: 5%
- Node Failures: 10%

Варьируйте Gossip Interval: 0.1, 0.2, 0.5, 1.0, 2.0 сек

**Заполните таблицу:**

| Gossip Interval | Время до "Хотя бы один узел знает" | Время до "Все живые узлы знают" | Макс. пропускная способность (Кбит/с) |
|-----------------|-----------------------------------|--------------------------------|---------------------------------------|
| 0.1 с | | | |
| 0.2 с | | | |
| 0.5 с | | | |
| 1.0 с | | | |
| 2.0 с | | | |

**Постройте графики:**
- График 1: Gossip Interval vs Время конвергенции
- График 2: Gossip Interval vs Пропускная способность

**Эксперимент 2: Масштабируемость системы**

Зафиксируйте параметры:
- Gossip Interval: 0.2 с
- Gossip Fanout: 3
- Packet Loss: 5%
- Node Failures: 10%

Варьируйте Nodes: 10, 25, 50, 100, 200

**Заполните таблицу и постройте графики аналогично Эксперименту 1**

**Эксперимент 3: Оптимизация Gossip Fanout**

Зафиксируйте параметры:
- Gossip Interval: 0.5 с
- Nodes: 100
- Packet Loss: 0%
- Node Failures: 5%

Варьируйте Gossip Fanout: 2, 3, 5, 7, 10

**Найдите оптимальное значение Fanout:**
- Минимальное время конвергенции при ограничении пропускной способности < 10 Кбит/с

**Эксперимент 4: Устойчивость к потере пакетов**

Зафиксируйте параметры:
- Gossip Interval: 0.2 с
- Gossip Fanout: 3
- Nodes: 50
- Node Failures: 5%

Варьируйте Packet Loss: 0%, 5%, 10%, 20%, 30%

**Проанализируйте:**
- При каком проценте потери пакетов система становится неработоспособной?
- Как изменяется время конвергенции?

#### Часть 3. Реализация Python-симулятора (30 баллов)

Реализуйте упрощенный симулятор для сравнения Serf Gossip с Heartbeat:

```python
import random
import time

class Node:
    def __init__(self, node_id):
        self.id = node_id
        self.alive = True
        self.knows_failure = False  # Знает ли узел об отказе

class GossipSimulator:
    def __init__(self, num_nodes, gossip_interval, gossip_fanout, packet_loss, node_failures_pct):
        """
        TODO: Инициализировать симулятор
        - Создать N узлов
        - Случайно выбрать node_failures_pct% узлов и пометить как отказавшие
        - Один из живых узлов изначально знает об отказе
        """
        self.nodes = []
        self.gossip_interval = gossip_interval
        self.gossip_fanout = gossip_fanout
        self.packet_loss = packet_loss
        pass
    
    def simulate_round(self):
        """
        TODO: Симуляция одного раунда gossip
        Для каждого живого узла, который знает об отказе:
            1. Выбрать gossip_fanout случайных живых узлов
            2. С вероятностью (1 - packet_loss) передать информацию
            3. Обновить knows_failure для целевых узлов
        """
        pass
    
    def run_simulation(self):
        """
        TODO: Запустить симуляцию
        Возвращает:
            - time_first_knowledge: время до первого обнаружения (сек)
            - time_all_knowledge: время полной конвергенции (сек)
            - bandwidth_used: использованная пропускная способность (усл. единиц)
        """
        round_count = 0
        time_first = None
        time_all = None
        
        while not self.all_alive_nodes_know():
            self.simulate_round()
            round_count += 1
            
            current_time = round_count * self.gossip_interval
            
            if time_first is None and self.at_least_one_knows():
                time_first = current_time
            
            if current_time > 30:  # Таймаут 30 секунд
                break
        
        time_all = round_count * self.gossip_interval
        
        # Расчет пропускной способности
        # bandwidth = количество сообщений * размер сообщения
        bandwidth_used = self.calculate_bandwidth()
        
        return time_first, time_all, bandwidth_used
    
    def at_least_one_knows(self):
        """Проверка: хотя бы один живой узел знает об отказе"""
        pass
    
    def all_alive_nodes_know(self):
        """Проверка: все живые узлы знают об отказе"""
        pass
    
    def calculate_bandwidth(self):
        """
        TODO: Рассчитать использованную пропускную способность
        Формула: (число узлов × fanout × раундов × размер пакета) / время
        """
        pass

class HeartbeatSimulator:
    """
    TODO: Реализовать централизованный heartbeat-протокол
    - Каждый узел отправляет heartbeat серверу мониторинга каждые heartbeat_interval
    - Сервер обнаруживает отказ, если не получает heartbeat в течение timeout
    - Сервер оповещает все узлы об отказе
    """
    pass

# Функция для сравнения протоколов
def compare_protocols(num_nodes, node_failures_pct):
    """
    TODO: Сравнить Gossip и Heartbeat
    Запустить симуляции с идентичными параметрами
    Вернуть сравнительную таблицу
    """
    pass

# Запуск экспериментов
if __name__ == '__main__':
    # Эксперимент: 50 узлов, 10% отказов
    num_nodes = 50
    node_failures_pct = 10
    
    print("Сравнение протоколов обнаружения отказов")
    print("=" * 80)
    
    # Gossip
    gossip_sim = GossipSimulator(
        num_nodes=num_nodes,
        gossip_interval=0.2,
        gossip_fanout=3,
        packet_loss=0.05,
        node_failures_pct=node_failures_pct
    )
    gossip_results = gossip_sim.run_simulation()
    
    # Heartbeat
    heartbeat_sim = HeartbeatSimulator(
        num_nodes=num_nodes,
        heartbeat_interval=0.2,
        timeout=1.0,
        node_failures_pct=node_failures_pct
    )
    heartbeat_results = heartbeat_sim.run_simulation()
    
    # Вывод результатов
    print(f"\nGossip Protocol:")
    print(f"  Время первого обнаружения: {gossip_results[0]:.2f} сек")
    print(f"  Время полной конвергенции: {gossip_results[1]:.2f} сек")
    print(f"  Пропускная способность: {gossip_results[2]:.2f} усл. ед.")
    
    print(f"\nHeartbeat Protocol:")
    print(f"  Время первого обнаружения: {heartbeat_results[0]:.2f} сек")
    print(f"  Время полной конвергенции: {heartbeat_results[1]:.2f} сек")
    print(f"  Пропускная способность: {heartbeat_results[2]:.2f} усл. ед.")
```

**Требуется реализовать:**
1. Класс `GossipSimulator` с методами simulate_round, run_simulation
2. Класс `HeartbeatSimulator` для сравнения
3. Функцию сравнения протоколов с выводом результатов

#### Часть 4. Рекомендации для CloudMonitor (10 баллов)

**Требуется найти и обосновать:**

1. **Оптимальные параметры для CloudMonitor:**
   - Количество узлов: 100
   - Требование: обнаружение отказа < 5 сек
   - Ограничение: пропускная способность < 10 Кбит/с на узел
   - Условия: packet loss до 10%, node failures до 20%

   На основе экспериментов предложите:
   - Gossip Interval: ? сек
   - Gossip Fanout: ?
   - Timeout для определения отказа: ? сек

2. **Архитектура мониторинга:**
   - Выбор протокола: Gossip vs Heartbeat vs Hybrid
   - Топология: peer-to-peer vs hierarchical
   - Механизмы устранения ложных срабатываний
   - Интеграция с системой алертинга (например, PagerDuty)

3. **План обеспечения отказоустойчивости:**
   - Стратегия репликации данных (quorum-based)
   - Механизм автоматического восстановления (self-healing)
   - Сценарии split-brain и методы их предотвращения
   - Мониторинг метрик (Prometheus + Grafana):
     - Количество живых узлов
     - Время обнаружения последнего отказа
     - Ложные срабатывания за период

### Формат сдачи

**Файлы для предоставления:**
1. `protocol_analysis.md` - теоретический анализ с заполненными таблицами
2. `serf_experiments.xlsx` - результаты всех экспериментов с симулятором Serf
3. `graphs/` - папка с графиками (PNG/PDF)
4. `simulator.py` - реализация Python-симулятора
5. `recommendations.md` - рекомендации для CloudMonitor с обоснованиями

**Критерии оценки:**
- Полнота теоретического анализа (25%)
- Корректность экспериментов с Serf (35%)
- Качество реализации Python-симулятора (30%)
- Обоснованность рекомендаций (10%)

---

## Список рекомендуемой литературы

### Основная литература:

1. **M. van Steen and A.S. Tanenbaum.** *Distributed Systems*, 4th ed., distributed-systems.net, 2023.  
   URL: https://www.distributed-systems.net/index.php/books/ds4/  
   Главы: 1 (Introduction), 4 (Communication), 8 (Fault Tolerance)

2. **Стин ван М., Таненбаум Э. С.** *Распределенные системы* / пер. с англ. В. А. Яроцкого. – М.: ДМК Пресс, 2021. – 584 с.  
   Главы: Распределенные алгоритмы, Отказоустойчивость

3. **Бабичев С. Л., Коньков К. А.** *Распределенные системы*: учеб. пособие для вузов. – М.: Юрайт, 2020.  
   URL: https://urait.ru/bcode/457005

4. **Kuzmiakova A.** *Concurrent, Parallel and Distributed Computing*. e-book Edition, 2023.

### Дополнительная литература по практическим аспектам:

5. **Richardson C., Smith F.** *Microservices: From Design to Deployment*. Nginx, 2016.  
   *Практическое руководство по микросервисной архитектуре*

6. **Indrasiri K., Siriwardena P.** *Microservices for the Enterprise: Designing, Developing, and Deploying*. Apress, 2018.  
   *Корпоративные паттерны микросервисов*

7. **Newman S.** *Building Microservices: Designing Fine-Grained Systems*, 2nd ed. O'Reilly Media, 2021.  
   *Проектирование микросервисных систем*

8. **Fowler M.** *Patterns of Enterprise Application Architecture*. Addison-Wesley, 2002.  
   *Классические паттерны корпоративных приложений*

### Спецификации и документация:

9. **gRPC Documentation**: https://grpc.io/docs/  
   *Руководство по gRPC: proto3, streaming, error handling*

10. **Flask Documentation**: https://flask.palletsprojects.com/  
    *Официальная документация микрофреймворка Flask*

11. **Nginx Documentation**: https://nginx.org/en/docs/  
    *Конфигурирование Nginx: proxy, caching, load balancing*

12. **RabbitMQ Documentation**: https://www.rabbitmq.com/documentation.html  
    *Руководство по RabbitMQ: exchanges, queues, patterns*

13. **Serf Documentation**: https://www.serf.io/docs/  
    *Gossip protocol, cluster membership, failure detection*

14. **Docker Documentation**: https://docs.docker.com/  
    *Контейнеризация приложений, Docker Compose*

### Статьи и исследования:

15. **Das A., et al.** "SWIM: Scalable Weakly-consistent Infection-style Process Group Membership Protocol." *Proceedings of IEEE DSN*, 2002.  
    *Основополагающая работа по gossip-протоколам*

16. **Gilbert S., Lynch N.** "Brewer's conjecture and the feasibility of consistent, available, partition-tolerant web services." *ACM SIGACT News*, 33(2), 2002.  
    *Формальное доказательство CAP-теоремы*

17. **Chandra T. D., Toueg S.** "Unreliable failure detectors for reliable distributed systems." *Journal of the ACM*, 43(2), 1996.  
    *Классификация failure detectors*

### Онлайн-курсы и туториалы:

18. **Martin Kleppmann's Distributed Systems Lectures**: https://www.youtube.com/playlist?list=PLeKd45zvjcDFUEv_ohr_HdUFe97RItdiB  
    *Видеолекции по распределенным системам от автора "Designing Data-Intensive Applications"*

19. **gRPC Tutorial (Official)**: https://grpc.io/docs/languages/python/basics/  
    *Пошаговое руководство по gRPC на Python*

20. **RabbitMQ Tutorials**: https://www.rabbitmq.com/getstarted.html  
    *Практические примеры работы с RabbitMQ*

---

**Примечание по выполнению практических заданий:**

- Все задания выполняются индивидуально
- Код должен быть хорошо прокомментирован (на русском или английском языке)
- Отчеты оформляются в формате Markdown (.md) или PDF
- Графики строятся с использованием matplotlib, Plotly или Excel
- Рекомендуемая среда: Ubuntu 20.04+, Python 3.8+
- Проекты размещаются в Git-репозитории (GitHub/GitLab)
- Срок выполнения каждого задания: 2 недели
- Защита заданий проводится в формате демонстрации работающей системы + ответы на вопросы
