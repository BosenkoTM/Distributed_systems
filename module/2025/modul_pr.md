# Практические задания модульного экзамена
## Дисциплина: Распределенные системы
### Бакалавриат, 3 курс, направление "Бизнес-информатика"

---

## Общие указания

**Время выполнения:** 40 минут на одно задание

**Формат экзамена:**
- Каждому студенту выдается одно практическое задание (номер определяется случайным образом)
- Разрешается использовать документацию, справочные материалы, примеры из лабораторных работ
- Код должен быть работающим и содержать комментарии
- Необходимо ответить на все вопросы в задании

**Критерии оценки:**
- **Отлично (90-100%):** Полностью работающая реализация, корректные ответы на все вопросы, чистый код с комментариями
- **Хорошо (75-89%):** Работающая реализация с небольшими недочетами, правильные ответы на большинство вопросов
- **Удовлетворительно (60-74%):** Частично работающая реализация или корректная логика с ошибками в деталях
- **Неудовлетворительно (<60%):** Нерабочий код или отсутствие понимания основных концепций

**Технические требования:**
- Python 3.8+
- Все необходимые библиотеки должны быть установлены заранее (grpcio, Flask, pika)
- Код должен запускаться локально на Ubuntu 20.04+ или аналогичной системе

---

## Практическое задание №1. Реализация gRPC-сервиса

### Постановка задачи

Разработайте gRPC-сервис "ProductCatalog" для получения информации о товарах. Сервис должен поддерживать два метода:
- **GetProduct** (Unary RPC) - получение одного товара по ID
- **StreamProducts** (Server Streaming RPC) - получение потока товаров по категории

### Что требуется реализовать

**1. Proto-контракт (30 баллов)**

Создайте файл `product_service.proto`:

```protobuf
syntax = "proto3";
package catalog;

service ProductCatalog {
    // TODO: Определить два метода
}

message ProductRequest {
    // TODO: ID товара
}

message CategoryRequest {
    // TODO: название категории
}

message Product {
    // TODO: id, name, price, category
}
```

**2. Реализация сервера (40 баллов)**

Реализуйте `server.py` с базой данных в памяти:

```python
import grpc
from concurrent import futures
import product_service_pb2
import product_service_pb2_grpc
import time

class ProductCatalogServicer(product_service_pb2_grpc.ProductCatalogServicer):
    def __init__(self):
        self.products = [
            {"id": "1", "name": "Laptop", "price": 75000, "category": "Electronics"},
            {"id": "2", "name": "Phone", "price": 45000, "category": "Electronics"},
            {"id": "3", "name": "Book", "price": 500, "category": "Books"}
        ]
    
    def GetProduct(self, request, context):
        # TODO: Найти товар по ID, вернуть Product или ошибку NOT_FOUND
        pass
    
    def StreamProducts(self, request, context):
        # TODO: Отправить поток товаров по категории
        # Добавить задержку 0.5 сек между сообщениями
        pass

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    product_service_pb2_grpc.add_ProductCatalogServicer_to_server(
        ProductCatalogServicer(), server
    )
    server.add_insecure_port('[::]:50051')
    print("Сервер запущен на порту 50051")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
```

**3. Реализация клиента (30 баллов)**

Создайте `client.py`:

```python
import grpc
import product_service_pb2
import product_service_pb2_grpc

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = product_service_pb2_grpc.ProductCatalogStub(channel)
        
        # TODO: Вызвать GetProduct для ID="1"
        
        # TODO: Вызвать StreamProducts для category="Electronics"
        # Вывести каждый товар из потока

if __name__ == '__main__':
    run()
```

### Что нужно найти и проанализировать

1. **Время выполнения:**
   - Замерьте время выполнения GetProduct
   - Замерьте общее время получения потока из 2 товаров (StreamProducts)
   - Объясните разницу

2. **Обработка ошибок:**
   - Что произойдет при запросе несуществующего ID?
   - Как клиент должен обработать ошибку NOT_FOUND?

### Формат сдачи

1. `product_service.proto` - proto-контракт
2. `server.py` - реализация сервера
3. `client.py` - реализация клиента
4. Краткие ответы на вопросы (в комментариях к коду или отдельным файлом)

**Критерии оценки:**
- Корректность proto-файла (30%)
- Работающий сервер с обработкой ошибок (40%)
- Работающий клиент (30%)

---

## Практическое задание №2. Проектирование RESTful API

### Постановка задачи

Разработайте REST API на Flask для управления задачами (Task Manager). API должно поддерживать базовые CRUD операции.

### Что требуется реализовать

**Модель Task:**
```json
{
  "id": 1,
  "title": "Изучить gRPC",
  "status": "pending",
  "created_at": "2025-12-01T10:00:00"
}
```

**Endpoints для реализации (40 баллов):**

```python
from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

# База данных в памяти
tasks = [
    {"id": 1, "title": "Изучить gRPC", "status": "pending", 
     "created_at": "2025-12-01T10:00:00"},
    {"id": 2, "title": "Настроить Nginx", "status": "done", 
     "created_at": "2025-12-01T09:00:00"}
]
next_id = 3

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """TODO: Вернуть список всех задач"""
    pass

@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """TODO: Вернуть задачу по ID или 404"""
    pass

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """
    TODO: Создать задачу
    Обязательное поле: title
    Валидация: title не пустой
    Вернуть 201 и созданную задачу
    """
    pass

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """TODO: Обновить статус задачи (pending/done)"""
    pass

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """TODO: Удалить задачу, вернуть 204"""
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

**Тестирование с curl (30 баллов):**

Напишите команды curl для:

1. Получения всех задач:
```bash
# TODO: написать команду
```

2. Создания новой задачи:
```bash
# TODO: написать команду POST с JSON
```

3. Обновления статуса задачи с ID=1:
```bash
# TODO: написать команду PUT
```

**Базовая настройка Nginx (30 баллов):**

Создайте конфигурацию `/etc/nginx/sites-available/taskmanager`:

```nginx
server {
    listen 80;
    server_name localhost;

    location /api/ {
        # TODO: Настроить proxy_pass на Flask (localhost:5000)
        
        # TODO: Добавить заголовки:
        # proxy_set_header Host $host;
        # proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Что нужно найти и проанализировать

1. **HTTP коды состояния:**
   - Какой код вернется при успешном GET?
   - Какой код при создании задачи (POST)?
   - Какой код при запросе несуществующей задачи?

2. **Идемпотентность методов:**
   - Какие методы идемпотентны и почему?
   - Что произойдет при повторном DELETE?

3. **Через Nginx vs напрямую:**
   - Какие преимущества дает использование Nginx?

### Формат сдачи

1. `app.py` - реализация Flask API
2. `curl_commands.txt` - команды для тестирования
3. `taskmanager.conf` - конфигурация Nginx
4. Краткие ответы на вопросы

**Критерии оценки:**
- Корректная реализация всех endpoints (40%)
- Правильные curl команды (30%)
- Базовая настройка Nginx (30%)

---

## Практическое задание №3. Асинхронное взаимодействие через RabbitMQ

### Постановка задачи

Разработайте систему обработки заказов с асинхронным взаимодействием: Producer отправляет заказы в RabbitMQ, Consumer их обрабатывает.

### Что требуется реализовать

**Структура сообщения (JSON):**
```json
{
  "order_id": "ORD-001",
  "customer": "Иван Иванов",
  "amount": 5000,
  "status": "pending"
}
```

**1. Producer (30 баллов)**

```python
import pika
import json

class OrderProducer:
    def __init__(self):
        # TODO: Подключиться к RabbitMQ (localhost, user/password)
        # TODO: Объявить очередь 'orders' с durable=True
        pass
    
    def send_order(self, order_id, customer, amount):
        """
        TODO: Создать JSON сообщение
        TODO: Опубликовать в очередь 'orders'
        TODO: Сделать сообщение persistent
        """
        pass
    
    def close(self):
        # TODO: Закрыть соединение
        pass

# Пример использования
if __name__ == '__main__':
    producer = OrderProducer()
    producer.send_order("ORD-001", "Иван Иванов", 5000)
    producer.send_order("ORD-002", "Петр Петров", 3000)
    print("Заказы отправлены")
    producer.close()
```

**2. Consumer (40 баллов)**

```python
import pika
import json
import time

class OrderConsumer:
    def __init__(self):
        # TODO: Подключиться к RabbitMQ
        # TODO: Объявить очередь 'orders'
        # TODO: Настроить prefetch_count=1
        pass
    
    def callback(self, ch, method, properties, body):
        """
        TODO: Распарсить JSON
        TODO: Обработать заказ (имитация: sleep(2))
        TODO: Вывести информацию о заказе
        TODO: Подтвердить обработку (basic_ack)
        """
        pass
    
    def start_consuming(self):
        # TODO: Запустить прослушивание очереди
        pass

if __name__ == '__main__':
    consumer = OrderConsumer()
    print("Ожидание заказов...")
    consumer.start_consuming()
```

**3. Docker Compose (15 баллов)**

```yaml
version: '3.8'
services:
  rabbitmq:
    image: rabbitmq:3.13-management
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      # TODO: Добавить RABBITMQ_DEFAULT_USER и PASSWORD
```

### Что нужно найти и проанализировать (15 баллов)

**Эксперимент:**
1. Запустите RabbitMQ через docker-compose
2. Запустите Consumer
3. Запустите Producer и отправьте 5 заказов
4. Замерьте время от отправки первого до обработки последнего заказа

**Ответьте на вопросы:**

1. **Время обработки:**
   - Сколько времени заняла обработка 5 заказов?
   - Почему именно столько?

2. **Надежность:**
   - Что произойдет, если Consumer отключится во время обработки?
   - Какую роль играет `basic_ack`?

3. **Преимущества асинхронности:**
   - Чем асинхронная обработка лучше синхронной?
   - Когда стоит использовать RabbitMQ вместо прямых HTTP-вызовов?

### Формат сдачи

1. `producer.py` - Producer
2. `consumer.py` - Consumer  
3. `docker-compose.yml` - конфигурация RabbitMQ
4. Ответы на вопросы с замерами времени

**Критерии оценки:**
- Работающий Producer (30%)
- Работающий Consumer с правильной обработкой (40%)
- Docker Compose (15%)
- Качество анализа (15%)

---

## Практическое задание №4. Анализ протоколов обнаружения отказов

### Постановка задачи

Проанализируйте и сравните протоколы обнаружения отказов (Gossip vs Heartbeat) для распределенной системы мониторинга из 50 узлов.

### Исходные данные

**Параметры системы:**
- Количество узлов: N = 50
- Отказавших узлов: 10% (5 узлов)
- Потеря пакетов: 5%
- Размер пакета: 1024 байта

**Gossip протокол:**
- Gossip Interval: τ = 0.2 сек
- Gossip Fanout: k = 3

**Heartbeat протокол:**
- Heartbeat Interval: 0.2 сек
- Timeout: 1.0 сек

### Часть 1. Теоретический анализ (30 баллов)

**Заполните сравнительную таблицу:**

| Характеристика | Gossip (Serf) | Heartbeat (централизованный) |
|----------------|---------------|------------------------------|
| Время обнаружения первого отказа | ? | ? |
| Масштабируемость (Big-O) | O(?) | O(?) |
| Single point of failure | ? | ? |
| Устойчивость к разделению сети | ? | ? |

**Формулы для расчетов:**

1. **Время конвергенции Gossip:**
   ```
   T_convergence ≈ τ × log_k(N)
   T_convergence ≈ 0.2 × log_3(50) ≈ ?
   ```

2. **Использование полосы пропускания Gossip (на узел):**
   ```
   Bandwidth = (k × размер_пакета × 8 бит) / τ
   Bandwidth = (3 × 1024 × 8) / 0.2 ≈ ? Кбит/с
   ```

3. **Heartbeat пропускная способность:**
   ```
   Bandwidth_total = N × размер_пакета × 8 / interval
   Bandwidth_per_node = Bandwidth_total / N = ?
   ```

**Задание:** Рассчитайте все значения и заполните таблицу.

### Часть 2. Эксперименты с Serf Simulator (40 баллов)

Используйте симулятор: https://www.serf.io/docs/internals/simulator.html

**Эксперимент 1: Влияние Gossip Interval**

Зафиксируйте:
- Nodes = 50
- Gossip Fanout = 3
- Packet Loss = 5%
- Node Failures = 10%

Варьируйте Gossip Interval: 0.1, 0.2, 0.5, 1.0 сек

**Заполните таблицу:**

| Gossip Interval | Время до "Все узлы знают" | Макс. полоса (Кбит/с) |
|-----------------|---------------------------|----------------------|
| 0.1 с | | |
| 0.2 с | | |
| 0.5 с | | |
| 1.0 с | | |

**Эксперимент 2: Влияние количества узлов**

Зафиксируйте:
- Gossip Interval = 0.2 с
- Gossip Fanout = 3
- Packet Loss = 5%
- Node Failures = 10%

Варьируйте Nodes: 10, 25, 50, 100

**Заполните таблицу и ответьте:**
- Как изменяется время конвергенции при увеличении N в 10 раз?
- Соответствует ли это логарифмической зависимости?

### Часть 3. Python-расчеты (30 баллов)

Реализуйте функцию для расчета пропускной способности:

```python
def calculate_bandwidth(gossip_interval, gossip_fanout, nodes, 
                       packet_size=1024, overhead=1.2):
    """
    TODO: Рассчитать пропускную способность для Gossip протокола
    
    Формула:
    messages_per_second = nodes * fanout / interval
    bandwidth_bps = messages_per_second * packet_size * overhead * 8
    
    Возвращает: bandwidth в Кбит/с
    """
    pass

def compare_protocols(nodes=50):
    """
    TODO: Сравнить Gossip и Heartbeat
    
    Рассчитать для обоих протоколов:
    - Пропускную способность на узел
    - Общую пропускную способность
    
    Вывести сравнительную таблицу
    """
    pass

# Запуск
if __name__ == '__main__':
    # Эксперимент: варьировать Gossip Interval
    intervals = [0.1, 0.2, 0.5, 1.0]
    
    print("Gossip Interval | Пропускная способность")
    print("-" * 45)
    for interval in intervals:
        bandwidth = calculate_bandwidth(interval, 3, 50)
        print(f"{interval:^15} | {bandwidth:,.2f} Кбит/с")
    
    print("\n" + "="*45 + "\n")
    compare_protocols(nodes=50)
```

**Задание:** Реализуйте функции и запустите расчеты.

### Что нужно найти и проанализировать

**1. Оптимальные параметры (выберите на основе экспериментов):**

Для системы из 100 узлов с требованиями:
- Обнаружение отказа < 3 секунды
- Пропускная способность < 10 Кбит/с на узел

Рекомендуемые параметры:
- Gossip Interval: ? сек
- Gossip Fanout: ?
- Обоснование выбора: ?

**2. Сравнение протоколов:**

При каких условиях лучше использовать:
- Gossip: ?
- Heartbeat: ?

**3. Влияние потери пакетов:**

На основе Эксперимента с Packet Loss:
- При 0% потерь: время конвергенции = ? сек
- При 20% потерь: время конвергенции = ? сек
- Выводы: ?

### Формат сдачи

1. `analysis.md` - заполненные таблицы и расчеты
2. `bandwidth_calculator.py` - реализация функций
3. `recommendations.txt` - рекомендации по выбору параметров

**Критерии оценки:**
- Корректность теоретических расчетов (30%)
- Качество экспериментов с симулятором (40%)
- Реализация Python-функций (30%)

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


### Спецификации и документация:

5. **gRPC Documentation**: https://grpc.io/docs/  
   *Руководство по gRPC: proto3, streaming, error handling*

6. **Flask Documentation**: https://flask.palletsprojects.com/  
    *Официальная документация микрофреймворка Flask*

7. **Nginx Documentation**: https://nginx.org/en/docs/  
    *Конфигурирование Nginx: proxy, caching, load balancing*

8. **RabbitMQ Documentation**: https://www.rabbitmq.com/documentation.html  
    *Руководство по RabbitMQ: exchanges, queues, patterns*

9. **Serf Documentation**: https://www.serf.io/docs/  
    *Gossip protocol, cluster membership, failure detection*

10. **Docker Documentation**: https://docs.docker.com/  



---

**Примечание по выполнению практических заданий:**

- Все задания выполняются индивидуально.
- Код должен быть хорошо прокомментирован (на русском или английском языке).
- Отчеты оформляются в формате Markdown (.md) или PDF.
- Графики строятся с использованием matplotlib, Plotly или Excel.
- Рекомендуемая среда: Ubuntu 20.04+, Python 3.8+.
- Защита заданий проводится в формате демонстрации работающей системы + ответы на вопросы


# Практические задания модульного экзамена
## Дисциплина: «Распределенные системы»
## Группа: АБП-231

**Время выполнения:** 40 минут  
**Детальное описание заданий:** https://github.com/BosenkoTM/Distributed_systems/blob/main/module/2025/modul_pr.md

---

## Практическое задание №1. Реализация gRPC-сервиса

**Задача:** Разработайте gRPC-сервис "ProductCatalog" для получения информации о товарах.

**Требуется реализовать:**
- Proto-контракт с двумя методами: GetProduct (Unary RPC) и StreamProducts (Server Streaming RPC)
- Серверную часть с базой данных в памяти (минимум 3 товара)
- Клиентскую часть с вызовами обоих методов

**Проанализировать:**
- Время выполнения каждого типа RPC
- Обработку ошибок (запрос несуществующего товара)

**Формат сдачи:** `product_service.proto`, `server.py`, `client.py` + краткие ответы на вопросы

---

## Практическое задание №2. Проектирование RESTful API

**Задача:** Разработайте REST API на Flask для управления задачами (Task Manager).

**Требуется реализовать:**
- Базовые CRUD операции для задач (GET, POST, PUT, DELETE)
- Модель Task: id, title, status, created_at
- Валидацию входных данных и обработку ошибок
- Конфигурацию Nginx в качестве обратного прокси

**Проанализировать:**
- HTTP коды состояния для различных сценариев
- Идемпотентность методов
- Преимущества использования Nginx

**Формат сдачи:** `app.py`, `curl_commands.txt`, `taskmanager.conf` + краткие ответы

---

## Практическое задание №3. Асинхронное взаимодействие через RabbitMQ

**Задача:** Разработайте систему обработки заказов с асинхронным взаимодействием через брокер сообщений.

**Требуется реализовать:**
- Producer для отправки заказов в очередь RabbitMQ
- Consumer для обработки заказов из очереди (имитация обработки: sleep 2 сек)
- Docker Compose конфигурацию для запуска RabbitMQ
- Структуру JSON сообщения: order_id, customer, amount, status

**Проанализировать:**
- Время обработки 5 заказов
- Надежность доставки (роль basic_ack)
- Преимущества асинхронности над синхронными вызовами

**Формат сдачи:** `producer.py`, `consumer.py`, `docker-compose.yml` + замеры и ответы

---

## Практическое задание №4. Анализ протоколов обнаружения отказов

**Задача:** Проанализируйте и сравните протоколы обнаружения отказов (Gossip vs Heartbeat) для системы из 50 узлов.

**Исходные данные:**
- Узлов: 50, отказов: 10%, потеря пакетов: 5%
- Gossip: interval=0.2с, fanout=3
- Heartbeat: interval=0.2с, timeout=1.0с

**Требуется:**
- Заполнить сравнительную таблицу характеристик протоколов
- Рассчитать пропускную способность для Gossip (формулы предоставлены)
- Провести эксперименты с Serf Simulator (варьировать interval и количество узлов)
- Реализовать Python-функции для расчета bandwidth

**Проанализировать:**
- Оптимальные параметры для системы из 100 узлов
- Условия применения каждого протокола
- Влияние потери пакетов на время конвергенции

**Формат сдачи:** таблицы и расчеты, `bandwidth_calculator.py`, `recommendations.txt`

---

## Общие требования

**Оценивание:**
- Задание №1: proto-файл (30%), сервер (40%), клиент (30%)
- Задание №2: endpoints (40%), curl (30%), Nginx (30%)
- Задание №3: Producer (30%), Consumer (40%), Docker (15%), анализ (15%)
- Задание №4: расчеты (30%), эксперименты (40%), Python (30%)

**Технические требования:**
- Python 3.8+, Ubuntu 20.04+
- Предустановленные библиотеки: grpcio, grpcio-tools, Flask, pika
- Код должен быть работающим с комментариями

**Справочные материалы:** Разрешается использовать документацию, примеры из лабораторных работ

---
