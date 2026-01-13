# Лабораторная работа № 3-1
## Тема: Организация асинхронного взаимодействия микросервисов с помощью брокера сообщений RabbitMQ

### 🎯 Цель работы
Изучить и реализовать два ключевых подхода к взаимодействию между сервисами:
1.  **Синхронное прямое взаимодействие** с использованием **gRPC**.
2.  **Асинхронное взаимодействие** через брокер сообщений **RabbitMQ**.
3.  Освоить развертывание инфраструктурных компонентов с помощью **Docker**.

### 🛠 Инструменты и технологический стек
*   **Операционная система:** Ubuntu 20.04+ (рекомендуется).
*   **Язык программирования:** Python 3.10+.
*   **Библиотеки:**
    *   `grpcio`, `grpcio-tools` (для gRPC).
    *   `pika` (клиент для RabbitMQ).
*   **Инфраструктура:**
    *   **Docker** и **Docker Compose** (для запуска RabbitMQ).
    *   **RabbitMQ** (брокер сообщений).

---

## Часть 1. Синхронное взаимодействие (gRPC)

На этом этапе создаются два сервиса, общающихся напрямую в режиме "запрос-ответ".

### 📚 Теоретическая часть
**gRPC** — высокопроизводительный фреймворк, использующий **Protocol Buffers** для определения контракта сервиса (методов и типов данных). Позволяет вызывать методы на удаленном сервере так же просто, как локальные функции.

### 💻 Ход работы

1.  **Установка зависимостей:**
    ```bash
    pip install grpcio grpcio-tools
    ```

2.  **Создание контракта (`message_service.proto`):**
    ```protobuf
    syntax = "proto3";
    package message;

    service MessageService {
      rpc ProcessMessage (MessageRequest) returns (MessageResponse) {}
    }

    message MessageRequest {
      string text = 1;
    }

    message MessageResponse {
      string processed_text = 1;
    }
    ```

3.  **Генерация кода:**
    ```bash
    python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. message_service.proto
    ```

4.  **Реализация сервера (`grpc_server.py`):**
    ```python
    import grpc
    from concurrent import futures
    import message_service_pb2
    import message_service_pb2_grpc

    class MessageService(message_service_pb2_grpc.MessageServiceServicer):
        def ProcessMessage(self, request, context):
            processed_text = f"Обработано сервером: {request.text.upper()}"
            return message_service_pb2.MessageResponse(processed_text=processed_text)

    def serve():
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        message_service_pb2_grpc.add_MessageServiceServicer_to_server(MessageService(), server)
        server.add_insecure_port('[::]:50051')
        print("gRPC сервер запущен на порту 50051...")
        server.start()
        server.wait_for_termination()

    if __name__ == '__main__':
        serve()
    ```

5.  **Реализация клиента (`grpc_client.py`):**
    ```python
    import grpc
    import message_service_pb2
    import message_service_pb2_grpc

    def run():
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = message_service_pb2_grpc.MessageServiceStub(channel)
            response = stub.ProcessMessage(message_service_pb2.MessageRequest(text="hello, world!"))
        print(f"Клиент получил ответ: {response.processed_text}")

    if __name__ == '__main__':
        run()
    ```

---

## Часть 2. Асинхронное взаимодействие (RabbitMQ)

В этой части добавляется брокер сообщений для развязывания сервисов. Цепочка взаимодействия: **Producer -> RabbitMQ -> Consumer -> gRPC Server**.

### 📚 Теоретическая часть
**RabbitMQ** — брокер сообщений, реализующий паттерн очереди.
*   **Producer (Поставщик):** отправляет сообщения в очередь.
*   **Queue (Очередь):** буфер, хранящий сообщения.
*   **Consumer (Потребитель):** забирает сообщения из очереди и обрабатывает их.

### 💻 Ход работы

1.  **Запуск RabbitMQ через Docker Compose:**
    Создайте файл `docker-compose.yml`:
    ```yaml
    version: '3.8'
    services:
      rabbitmq:
        image: rabbitmq:3.9-management
        container_name: 'rabbitmq'
        ports:
          - "5672:5672"
          - "15672:15672"
        environment:
          - RABBITMQ_DEFAULT_USER=user
          - RABBITMQ_DEFAULT_PASS=password
    ```
    Запуск: `docker-compose up -d`

2.  **Создание Producer (`producer.py`):**
    Отправляет задачи в очередь `task_queue`.
    ```python
    import pika, sys

    credentials = pika.PlainCredentials('user', 'password')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue='task_queue', durable=True)

    message = ' '.join(sys.argv[1:]) or "New Task!"
    channel.basic_publish(
        exchange='', routing_key='task_queue', body=message,
        properties=pika.BasicProperties(delivery_mode=2))
    print(f" [x] Отправлено: '{message}'")
    connection.close()
    ```

3.  **Создание Consumer (`consumer.py`):**
    Слушает очередь и вызывает gRPC-сервис.
    ```python
    import pika, grpc
    import message_service_pb2, message_service_pb2_grpc

    def process_message_via_grpc(text):
        try:
            with grpc.insecure_channel('localhost:50051') as channel:
                stub = message_service_pb2_grpc.MessageServiceStub(channel)
                response = stub.ProcessMessage(message_service_pb2.MessageRequest(text=text))
            return response.processed_text
        except grpc.RpcError as e:
            return f"Ошибка gRPC: {e.details()}"

    def main():
        credentials = pika.PlainCredentials('user', 'password')
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', credentials=credentials))
        channel = connection.channel()
        channel.queue_declare(queue='task_queue', durable=True)

        def callback(ch, method, properties, body):
            print(f" [x] Получено: {body.decode()}")
            result = process_message_via_grpc(body.decode())
            print(f" [✓] Результат: {result}")
            ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue='task_queue', on_message_callback=callback)
        print(' [*] Ожидание сообщений...')
        channel.start_consuming()

    if __name__ == '__main__':
        main()
    ```

---

### 📝 Варианты заданий

Необходимо реализовать три метода в gRPC сервисе и обеспечить их вызов через RabbitMQ согласно вашему варианту.

[🔗 Перейти к списку вариантов заданий на образовательном портале](https://envlab.ru/mod/assign/view.php?id=1019&forceview=1)

---

### 📄 Требования к отчету

Отчет оформляется в файле `readme.md` в корне репозитория:
1.  **Постановка задачи:** Описание решаемой проблемы.
2.  **Вариант:** Номер и текст задания.
3.  **Архитектура:**
    *   Схема и описание Части 1 (gRPC).
    *   Схема и описание Части 2 (RabbitMQ + gRPC).
    *   Код `docker-compose.yml`.
4.  **Стек технологий:** Перечень инструментов.
5.  **Скриншоты:** Демонстрация работы (Server, Consumer, Producer, логи).

### 💯 Критерии оценки

| Баллы | Критерии |
|---|---|
| **20%** | **Часть 1 (gRPC):** Клиент и сервер запускаются и взаимодействуют. |
| **50%** | **Часть 2 (RabbitMQ):** Брокер в Docker, Producer отправляет, Consumer получает и вызывает gRPC. Выполнены все 3 задания варианта. |
| **30%** | **Отчет и код:** Качественный `readme.md`, читаемый код, использование Ubuntu 20.04+. |

---

### 💡 Пример реализации (Вариант 30)

**Задача:**
1.  gRPC-сервис с методами: `AssignAB` (A/B тестирование), `Factorial` (факториал), `MostFrequentLetter` (частая буква).
2.  RabbitMQ Producer отправляет сообщения с префиксами: `user_id`, `fact:N`, `freq:TEXT`.

**Структура проекта:**
```text
├── grpc_sync/
│   ├── message_service.proto   # Контракт с 3 методами
│   ├── grpc_server.py          # Реализация логики методов
│   └── grpc_client.py          # Тестовый клиент
├── rabbitmq_async/
│   ├── docker-compose.yml      # RabbitMQ
│   ├── producer.py             # Парсит аргументы и шлёт в очередь
│   └── consumer.py             # Читает очередь, парсит префикс, вызывает нужный метод gRPC
```

**Алгоритм запуска:**
1.  **Терминал 1:** `cd grpc_sync && python grpc_server.py` (Запуск gRPC сервера).
2.  **Терминал 2:** `cd rabbitmq_async && docker-compose up -d` (Запуск брокера).
3.  **Терминал 3:** `cd rabbitmq_async && python consumer.py` (Запуск слушателя).
4.  **Терминал 4:** `cd rabbitmq_async && python producer.py fact:5` (Отправка задачи).
    *   *Результат в Терминале 3:* `[✓] Результат: 120`.
