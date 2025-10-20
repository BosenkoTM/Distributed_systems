
## Постановка задачи (Вариант 30)

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