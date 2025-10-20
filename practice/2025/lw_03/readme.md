# Лабораторная работа 3. Организация асинхронного взаимодействия микросервисов с помощью брокера сообщений RabbitMQ

**Цель работы:** изучить и реализовать два ключевых подхода к взаимодействию между сервисами: синхронное прямое взаимодействие с использованием gRPC и асинхронное взаимодействие через брокер сообщений RabbitMQ. Освоить развертывание инфраструктурных компонентов с помощью Docker.

---

## Часть 1. Синхронное взаимодействие с использованием gRPC (без брокера)

На этом этапе мы создадим два сервиса, которые общаются друг с другом напрямую в режиме "запрос-ответ". Это синхронный паттерн, где клиент отправляет запрос и ждет ответа от сервера.

### Теоретическая часть

**gRPC** — это современный высокопроизводительный фреймворк с открытым исходным кодом, который может работать в любой среде. Он позволяет эффективно соединять сервисы в центрах обработки данных и между ними с поддержкой балансировки нагрузки, трассировки, проверки работоспособности и аутентификации. Основная идея заключается в определении контракта сервиса (методов, которые можно вызывать удаленно, с их параметрами и типами возвращаемых данных) с помощью Protocol Buffers.

### Алгоритм выполнения работы
- Определить контракт сервиса с помощью файла `.proto`.
- Сгенерировать код на Python из `.proto` файла.
- Реализовать gRPC сервер, который будет выполнять логику обработки запроса.
- Реализовать gRPC клиент, который будет отправлять запросы на сервер.
- Протестировать прямое взаимодействие клиента и сервера.

### Пример решения

1.  **Установите необходимые библиотеки:**
    ```bash
    pip install grpcio grpcio-tools
    ```
2.  **Создайте файл контракта `message_service.proto`:**
    ```protobuf
    syntax = "proto3";

    package message;

    // Определение сервиса
    service MessageService {
      // Метод, который принимает запрос и возвращает ответ
      rpc ProcessMessage (MessageRequest) returns (MessageResponse) {}
    }

    // Структура сообщения-запроса
    message MessageRequest {
      string text = 1;
    }

    // Структура сообщения-ответа
    message MessageResponse {
      string processed_text = 1;
    }
    ```
3.  **Сгенерируйте gRPC код:**
    ```bash
    python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. message_service.proto
    ```
    *(В директории появятся файлы `message_service_pb2.py` и `message_service_pb2_grpc.py`)*

4.  **Создайте файл сервера `grpc_server.py`:**
    ```python
    import grpc
    from concurrent import futures
    import message_service_pb2
    import message_service_pb2_grpc

    # Класс-сервис, наследуется от сгенерированного и реализует его методы
    class MessageService(message_service_pb2_grpc.MessageServiceServicer):
        def ProcessMessage(self, request, context):
            # Простая логика: переводим текст в верхний регистр
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
5.  **Создайте файл клиента `grpc_client.py`:**
    ```python
    import grpc
    import message_service_pb2
    import message_service_pb2_grpc

    def run():
        # Устанавливаем соединение с сервером
        with grpc.insecure_channel('localhost:50051') as channel:
            # Создаем "заглушку" (stub) для вызова удаленных процедур
            stub = message_service_pb2_grpc.MessageServiceStub(channel)
            # Вызываем удаленный метод ProcessMessage
            response = stub.ProcessMessage(message_service_pb2.MessageRequest(text="hello, world!"))
        print(f"Клиент получил ответ: {response.processed_text}")

    if __name__ == '__main__':
        run()
    ```
6.  **Тестирование:**
    *   В одном терминале запустите сервер: `python grpc_server.py`
    *   В другом терминале запустите клиент: `python grpc_client.py`
    *   Убедитесь, что клиент успешно получил обработанное сервером сообщение.

---

## Часть 2. Асинхронное взаимодействие через брокер сообщений RabbitMQ

Теперь мы усложним архитектуру, добавив брокер сообщений. Это позволит нашим сервисам общаться асинхронно и быть независимыми друг от друга. Один сервис (Producer) будет публиковать сообщения в очередь, а другой (Consumer) — забирать их для обработки, используя gRPC-сервис из Части 1. RabbitMQ мы развернем с помощью Docker.

### Теоретическая часть

**RabbitMQ** — это брокер сообщений, который принимает и пересылает сообщения. Вы можете думать о нем как о почтовом отделении: когда вы кладете письмо в почтовый ящик, вы уверены, что почтальон в конечном итоге доставит его получателю. RabbitMQ работает по тому же принципу, используя очереди для хранения сообщений до тех пор, пока их не заберет сервис-получатель (Consumer). Это позволяет создавать отказоустойчивые и масштабируемые системы.

**Docker** — это платформа для разработки, доставки и запуска приложений в контейнерах. Мы будем использовать `docker-compose` для простого описания и запуска RabbitMQ в изолированной среде.

### Алгоритм выполнения работы
1.  Установить Docker и Docker Compose.
2.  Создать `docker-compose.yml` файл для запуска RabbitMQ.
3.  Запустить контейнер с RabbitMQ.
4.  Создать Producer на Python, который отправляет сообщения в очередь RabbitMQ.
5.  Создать Consumer на Python, который читает сообщения из очереди и для их обработки вызывает gRPC сервис, созданный в Части 1.
6.  Протестировать всю цепочку: Producer -> RabbitMQ -> Consumer -> gRPC Server.

### Пример решения
1.  **Создайте файл `docker-compose.yml`:**
    ```yaml
    version: '3.8'
    services:
      rabbitmq:
        image: rabbitmq:3.9-management
        container_name: 'rabbitmq'
        ports:
          - "5672:5672"  # Порт для подключения клиентов
          - "15672:15672" # Порт для веб-интерфейса управления
        environment:
          - RABBITMQ_DEFAULT_USER=user
          - RABBITMQ_DEFAULT_PASS=password
    ```
2.  **Запустите RabbitMQ:**
    *   Откройте терминал в директории с файлом `docker-compose.yml` и выполните команду:
        ```bash
        docker-compose up -d
        ```
    *   Вы можете открыть веб-интерфейс в браузере по адресу `http://localhost:15672` (логин: `user`, пароль: `password`).

3.  **Создайте Producer (`producer.py`):**
    *   Установите библиотеку: `pip install pika`
    ```python
    import pika
    import sys

    # Учетные данные для подключения
    credentials = pika.PlainCredentials('user', 'password')
    # Подключаемся к RabbitMQ в Docker
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', credentials=credentials))
    channel = connection.channel()

    # Создаем очередь 'task_queue'
    channel.queue_declare(queue='task_queue', durable=True)

    message = ' '.join(sys.argv[1:]) or "New Task!"
    # Публикуем сообщение
    channel.basic_publish(
        exchange='',
        routing_key='task_queue',
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # делаем сообщение постоянным
        ))
    print(f" [x] Отправлено сообщение: '{message}'")
    connection.close()
    ```
4.  **Создайте Consumer (`consumer.py`):**
    *   Этот скрипт будет слушать очередь и вызывать gRPC-сервер из Части 1 для обработки.
    ```python
    import pika
    import grpc
    import message_service_pb2
    import message_service_pb2_grpc

    def process_message_via_grpc(text):
        """Функция для вызова gRPC сервиса."""
        try:
            with grpc.insecure_channel('localhost:50051') as channel:
                stub = message_service_pb2_grpc.MessageServiceStub(channel)
                response = stub.ProcessMessage(message_service_pb2.MessageRequest(text=text))
            return response.processed_text
        except grpc.RpcError as e:
            return f"Ошибка вызова gRPC: {e.details()}"

    def main():
        credentials = pika.PlainCredentials('user', 'password')
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', credentials=credentials))
        channel = connection.channel()

        channel.queue_declare(queue='task_queue', durable=True)
        print(' [*] Ожидание сообщений. Для выхода нажмите CTRL+C')

        def callback(ch, method, properties, body):
            message_text = body.decode()
            print(f" [x] Получено сообщение: {message_text}")

            # Обрабатываем сообщение с помощью gRPC
            processed_result = process_message_via_grpc(message_text)
            print(f" [✓] Результат обработки: {processed_result}")

            ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue='task_queue', on_message_callback=callback)

        channel.start_consuming()

    if __name__ == '__main__':
        main()
    ```
5.  **Тестирование:**
    1.  Запустите RabbitMQ через Docker (если еще не запущен): `docker-compose up -d`
    2.  Запустите gRPC сервер из Части 1: `python grpc_server.py`
    3.  Запустите Consumer в новом терминале: `python consumer.py`
    4.  Запустите Producer в еще одном терминале для отправки сообщения: `python producer.py "Это тестовое задание для обработки"`
    5.  Проверьте логи Consumer'а — он должен получить сообщение и вывести результат, обработанный gRPC-сервером.

---

## Варианты заданий
Выберите один из вариантов ниже. Для каждого варианта необходимо реализовать все три задания, используя архитектуру Части 1 из Части 2 (Producer -> RabbitMQ -> Consumer -> gRPC Server).

[Варианты заданий на образовательном портале](http://95.131.149.21/moodle/mod/assign/view.php?id=1775)

---
## Отчет

Проект необходимо оформить в виде файла `readme.md` в корне вашего репозитория. Отчет должен содержать следующие разделы:

- **Постановка задачи**. Краткое описание бизнес-проблемы, которую решает разработанная система.
- **Вариант**. Укажите номер вашего варианта и приведите тексты трех заданий.
- **Архитектура**:
    - **Часть 1 (gRPC)**. Представьте диаграмму и описание синхронного взаимодействия клиента и сервера.
    - **Часть 2 (RabbitMQ)**. Представьте диаграмму, иллюстрирующую взаимодействие компонентов (Producer, RabbitMQ, Consumer, gRPC Server). Опишите логику работы каждого компонента и преимущества асинхронного подхода для вашего варианта.
    - Приведите содержимое вашего файла `docker-compose.yml`.
- **Стек технологий**. Перечислите все использованные языки программирования, библиотеки, фреймворки и инструменты (Ubuntu 20.04+, Python, gRPC, Pika, Docker).
- **Основные скрины**. Приложите скриншоты, демонстрирующие работу всей системы:
    - Запущенный gRPC сервер.
    - Запущенный Consumer в режиме ожидания.
    - Терминал, где Producer отправляет сообщение.
    - Терминал Consumer'а с логами получения и обработки сообщения.

---

## Критерии оценки
- **Корректность реализации Части 1 (20%):**
    - gRPC клиент и сервер успешно запускаются и корректно взаимодействуют.
- **Корректность реализации Части 2 (50%):**
    - RabbitMQ успешно развернут с помощью Docker.
    - Producer корректно отправляет сообщения в очередь.
    - Consumer корректно получает сообщения и вызывает gRPC сервис для их обработки.
    - Все три задания выбранного варианта выполнены.
- **Качество отчета и кода (30%):**
    - Файл `readme.md` содержит все необходимые разделы, информация изложена ясно и полно.
    - Код хорошо структурирован, читаем и содержит необходимые комментарии.
    - Работа выполняется в среде **Ubuntu 20.04+**.


## Пример решения (Вариант 30)

Необходимо реализовать две концепции обмена сообщениями между микросервисами для варианта 30:

- Синхронное взаимодействие (gRPC): клиент напрямую вызывает gRPC‑сервис с тремя методами — назначение группы A/B по `user_id`, вычисление факториала и поиск самой частой буквы в тексте.
- Асинхронное взаимодействие (RabbitMQ): Producer публикует сообщения в очередь, Consumer читает их и вызывает соответствующий метод gRPC‑сервиса. Сообщения имеют формат:
  - `user_id` — для A/B назначения (по умолчанию любые строки без префикса);
  - `fact:N` — для факториала числа `N`;
  - `freq:TEXT` — для поиска самой частой буквы в `TEXT`.

Требуется продемонстрировать обе архитектуры, сравнить их свойства (связанность, устойчивость к отказам, масштабирование), и оформить запуск в виде пошаговых инструкций.

## Архитектура

### Часть 1. Синхронная (gRPC)
Клиент вызывает удалённые процедуры gRPC‑сервера по контракту `message_service.proto`:
- `AssignAB(ABRequest) -> ABResponse`
- `Factorial(FactorialRequest) -> FactorialResponse`
- `MostFrequentLetter(TextRequest) -> LetterResponse`

Ключевые свойства: простота, низкая задержка, высокая связанность (клиент зависит от доступности сервера).

Схема:
```
Client (grpc_client.py)
        |
        |  gRPC (HTTP/2)
        v
Server (grpc_server.py)
```

### Часть 2. Асинхронная (RabbitMQ + gRPC)
Поток: `Producer -> RabbitMQ queue -> Consumer -> gRPC Server`.
- Producer публикует задачи в очередь `task_queue`.
- Consumer обрабатывает сообщения и прозрачно делегирует вычисления gRPC‑сервису.
- Преимущества: декуплинг, буферизация нагрузки, ретраи за счёт подтверждений `ack`, масштабирование Consumers.

Схема:
```
Producer (producer.py, web_app.py)  --publish-->  RabbitMQ (task_queue)
                                                     |
                                                     |  consume
                                                     v
                                             Consumer (consumer.py)
                                                     |
                                                     |  gRPC (HTTP/2)
                                                     v
                                             gRPC Server (grpc_server.py)
```

## Стек технологий
- Python 3.10+
- gRPC (`grpcio`, `grpcio-tools`)
- RabbitMQ (Docker, образ `rabbitmq:3.12-management`), клиент `pika`
- Docker Compose

## Структура репозитория
- `grpc_sync/`:
  - `message_service.proto` — контракт.
  - `grpc_server.py` — сервер.
  - `grpc_client.py` — клиент‑пример.
- `rabbitmq_async/`:
  - `docker-compose.yml` — брокер RabbitMQ.
  - `producer.py` — отправка сообщений.
  - `consumer.py` — чтение и делегирование в gRPC.

## Шаги выполнения

1) Установка и активация виртуального окружения, установка зависимостей:
```bash
sudo apt update
sudo apt install -y python3-venv python3-pip
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install grpcio grpcio-tools pika flask
# Деактивация окружения после работы:  deactivate
```

2) Генерация gRPC‑кода (из каталога `grpc_sync`, в активированном venv):
```bash
cd grpc_sync
# убедитесь, что активировано виртуальное окружение
# если требуется, активируйте его:  source ../.venv/bin/activate
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. message_service.proto
cd ..
```

3) Запуск gRPC‑сервера (в терминале 1):
```bash
cd grpc_sync
python grpc_server.py
```

4) Тест синхронного вызова (в терминале 2):
```bash
cd grpc_sync
# активируйте venv в этом терминале, если он не активен
source ../.venv/bin/activate
python grpc_client.py
```

5) Запуск RabbitMQ (в терминале 3):
```bash
cd rabbitmq_async
# Вариант 1
docker compose up -d
# или, если используется старая утилита
# docker-compose up -d
```

6) Запуск Consumer (в терминале 4):
        ```bash
cd rabbitmq_async
python consumer.py
```

7) Веб‑приложение для публикации и просмотра результатов (в терминале 5):
```bash
cd rabbitmq_async
python web_app.py
```
Откройте `http://127.0.0.1:8080` — отправляйте сообщения (`user42`, `fact:6`, `freq:abracadabra`) и обновляйте страницу, чтобы увидеть результаты из БД.

8) Отправка сообщений Producer‑ом из CLI (альтернатива вебу, в терминале 6):
```bash
cd rabbitmq_async
python producer.py user42
python producer.py fact:6
python producer.py freq:abracadabra
```

Ожидаемо Consumer выведет ответы gRPC‑сервиса для каждого сообщения.

### Веб‑интерфейс RabbitMQ (Management)
- Откройте `http://localhost:15672` и войдите (логин `user`, пароль `password`).
- На вкладке Queues проверьте очередь `task_queue` (входящие/обработанные сообщения, потребители).

## Последовательность запуска (полная с RabbitMQ)

1) Активировать виртуальное окружение в каждом терминале перед командами:
```bash
source .venv/bin/activate
```

2) Терминал 1 — gRPC сервер:
```bash
cd grpc_sync
python grpc_server.py
```

3) Терминал 2 — RabbitMQ и Consumer:
```bash
cd rabbitmq_async
docker compose up -d
# при необходимости можно указать явную цель gRPC (например, если IPv6 localhost мешает):
# export GRPC_TARGET=127.0.0.1:50051
python consumer.py
```

4) Терминал 3 — Веб‑приложение:
```bash
cd rabbitmq_async
python web_app.py
```
Проверка: открыть `http://127.0.0.1:8080` и отправить задачи `user42`, `fact:6`, `freq:abracadabra` (можно одной строкой через запятую). Результаты появятся в таблице.

5) (Опционально) Терминал 4 — CLI‑producer:
```bash
cd rabbitmq_async
# export GRPC_TARGET=127.0.0.1:50051
python producer.py user42
python producer.py fact:6
python producer.py freq:abracadabra
```

6) Проверка в RabbitMQ UI:
- Открыть `http://localhost:15672` (user/password)
- Перейти Queues → `task_queue`
- Смотреть Ready/Unacked/Total, Consumers, графики сообщений; при отправке через веб/CLI счётчики растут и уменьшаются по мере обработки

### Обновлённый порядок запуска

- Терминал 1 (venv):
```bash
cd grpc_sync && source ../.venv/bin/activate && python grpc_server.py
```

- Терминал 2 (venv):
```bash
cd rabbitmq_async && source ../.venv/bin/activate && docker compose up -d && python consumer.py
```

- Терминал 3 (venv):
```bash
cd rabbitmq_async && source ../.venv/bin/activate && python web_app.py
```
Затем открыть `http://127.0.0.1:8080`.

Отправляйте одно или несколько заданий: `user42`, `fact:6`, `freq:abracadabra` или строку с запятыми. Результаты видны в вебе и в консоли consumer’а.

---

