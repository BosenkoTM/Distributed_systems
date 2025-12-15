import time
import redis
# #region agent log
import json
import os
log_path = '/home/mgpu/Downloads/ds/lb_06/.cursor/debug.log'
def log_debug(msg, data=None, hypothesis_id="A"):
    try:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, 'a') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"post-fix","hypothesisId":hypothesis_id,"location":"app.py","message":msg,"data":data or {},"timestamp":int(time.time()*1000)}) + '\n')
    except: pass
log_debug("Starting app import", {"step":"before_flask_import"})
# #endregion
from flask import Flask
# #region agent log
try:
    import werkzeug
    import flask
    log_debug("Versions check", {"flask_version":flask.__version__,"werkzeug_version":werkzeug.__version__})
except Exception as e:
    log_debug("Version check failed", {"error":str(e)})
# #endregion

app = Flask(__name__)
# 'redis' - это имя хоста (контейнера), которое мы укажем в docker-compose
cache = redis.Redis(host='redis', port=6379)

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

@app.route('/')
def hello():
    count = get_hit_count()
    
    # Проверка на "Счастливого посетителя" (кратно 7)
    if count % 7 == 0:
        return '<h1 style="color:green">Поздравляем! Вы счастливчик!</h1><p style="color:green; font-size:20px;">Вы посетитель номер: <strong>{}</strong></p>'.format(count)
    else:
        return '<h1>Посетитель номер: <strong>{}</strong></h1>'.format(count)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)

