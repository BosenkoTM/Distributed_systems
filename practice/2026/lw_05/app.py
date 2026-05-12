import time
import redis
import json
import os
from datetime import datetime
from flask import Flask

# -------------------------------
# Настройка путей и логирования
# -------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOG_DIR = os.path.join(BASE_DIR, "logs")

# Создание папки logs автоматически
os.makedirs(LOG_DIR, exist_ok=True)

log_path = os.path.join(LOG_DIR, "debug.log")


def log_debug(msg, data=None, hypothesis_id="APP"):
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "sessionId": "distributed-system",
                "runId": "docker-compose",
                "hypothesisId": hypothesis_id,
                "location": "app.py",
                "message": msg,
                "data": data or {},
                "timestamp": int(time.time() * 1000),
                "datetime": datetime.now().isoformat()
            }, ensure_ascii=False) + "\n")

    except Exception as exc:
        print("Logging error:", exc)


log_debug("Application started")

# -------------------------------
# Flask application
# -------------------------------

app = Flask(__name__)

# redis — имя контейнера в docker-compose.yml
cache = redis.Redis(
    host="redis",
    port=6379,
    decode_responses=True
)

# -------------------------------
# Работа со счетчиком
# -------------------------------

def get_hit_count():

    retries = 5

    while True:

        try:
            count = cache.incr("hits")

            log_debug(
                "Counter incremented",
                {"count": count},
                hypothesis_id="COUNTER"
            )

            return count

        except redis.exceptions.ConnectionError as exc:

            log_debug(
                "Redis connection error",
                {
                    "error": str(exc),
                    "retries_left": retries
                },
                hypothesis_id="REDIS"
            )

            if retries == 0:
                raise exc

            retries -= 1
            time.sleep(0.5)

# -------------------------------
# Бизнес-логика
# -------------------------------

def get_decision(count):

    # Супер-приз
    if count % 21 == 0:
        return {
            "title": "Супер-приз!",
            "message": "Вы легендарный посетитель системы!",
            "color": "#8e44ad",
            "emoji": "👑"
        }

    # Юбилей
    if count % 10 == 0:
        return {
            "title": "Юбилейный посетитель!",
            "message": "Поздравляем с круглым номером.",
            "color": "#2980b9",
            "emoji": "🎯"
        }

    # Счастливчик
    if count % 7 == 0:
        return {
            "title": "Счастливый посетитель!",
            "message": "Сегодня удача на вашей стороне.",
            "color": "#27ae60",
            "emoji": "🍀"
        }

    # Чётный пользователь
    if count % 2 == 0:
        return {
            "title": "Чётный посетитель",
            "message": "Система обработала запрос успешно.",
            "color": "#555",
            "emoji": "⚙️"
        }

    # Обычный режим
    return {
        "title": "Обычный посетитель",
        "message": "Запрос обработан распределённой системой.",
        "color": "#333",
        "emoji": "👋"
    }

# -------------------------------
# Главная страница
# -------------------------------

@app.route("/")
def hello():

    count = get_hit_count()

    decision = get_decision(count)

    log_debug(
        "Decision selected",
        {
            "count": count,
            "decision": decision["title"]
        },
        hypothesis_id="DECISION"
    )

    return f"""
    <!DOCTYPE html>
    <html lang="ru">

    <head>
        <meta charset="UTF-8">
        <title>Distributed App</title>

        <style>

            body {{
                font-family: Arial, sans-serif;
                background: #f4f6f8;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }}

            .card {{
                background: white;
                padding: 40px;
                border-radius: 18px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.12);
                text-align: center;
                max-width: 520px;
            }}

            .emoji {{
                font-size: 64px;
            }}

            h1 {{
                color: {decision["color"]};
            }}

            .count {{
                font-size: 30px;
                font-weight: bold;
                color: {decision["color"]};
            }}

            .message {{
                font-size: 18px;
                color: #555;
            }}

            .footer {{
                margin-top: 20px;
                font-size: 13px;
                color: #888;
            }}

        </style>
    </head>

    <body>

        <div class="card">

            <div class="emoji">
                {decision["emoji"]}
            </div>

            <h1>
                {decision["title"]}
            </h1>

            <p class="message">
                {decision["message"]}
            </p>

            <p>
                Вы посетитель номер:
            </p>

            <div class="count">
                {count}
            </div>

            <div class="footer">
                Логи сохраняются в:
                <strong>logs/debug.log</strong>
            </div>

        </div>

    </body>

    </html>
    """

# -------------------------------
# Healthcheck endpoint
# -------------------------------

@app.route("/health")
def health():

    try:

        cache.ping()

        log_debug(
            "Health check OK",
            hypothesis_id="HEALTH"
        )

        return {
            "status": "ok",
            "redis": "connected"
        }

    except Exception as exc:

        log_debug(
            "Health check failed",
            {"error": str(exc)},
            hypothesis_id="HEALTH"
        )

        return {
            "status": "error",
            "redis": "disconnected"
        }, 500

# -------------------------------
# Запуск приложения
# -------------------------------

if __name__ == "__main__":

    log_debug("Flask application started")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )