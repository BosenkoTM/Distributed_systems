from flask import Flask, request, redirect, url_for, render_template_string
import pika
from storage import init_db, fetch_recent


app = Flask(__name__)


HTML = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>RabbitMQ Demo</title>
    <style>
      body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 24px; }
      form { margin-bottom: 24px; display: flex; gap: 8px; }
      input[type=text] { flex: 1; padding: 8px; }
      button { padding: 8px 12px; }
      table { border-collapse: collapse; width: 100%; }
      th, td { border: 1px solid #ddd; padding: 8px; }
      th { background: #f7f7f7; text-align: left; }
      caption { text-align: left; font-weight: 600; margin-bottom: 8px; }
      .hint { color: #666; font-size: 14px; }
    </style>
  </head>
  <body>
    <h1>RabbitMQ Tasks</h1>
    <p class="hint">Examples: <code>user42</code>, <code>fact:6</code>, <code>freq:abracadabra</code></p>
    <form method="post" action="{{ url_for('publish') }}">
      <input type="text" name="message" placeholder="Enter message" required />
      <button type="submit">Publish</button>
      <a href="{{ url_for('index') }}">Refresh</a>
    </form>

    <table>
      <caption>Last results</caption>
      <thead>
        <tr><th>ID</th><th>Created</th><th>Message</th><th>Method</th><th>Result</th></tr>
      </thead>
      <tbody>
        {% for r in rows %}
        <tr>
          <td>{{ r[0] }}</td>
          <td>{{ r[1] }}</td>
          <td>{{ r[2] }}</td>
          <td>{{ r[3] }}</td>
          <td>{{ r[4] }}</td>
        </tr>
        {% else %}
        <tr><td colspan="5">No results yet</td></tr>
        {% endfor %}
      </tbody>
    </table>

    <p class="hint">RabbitMQ UI: <a href="http://localhost:15672" target="_blank">http://localhost:15672</a> (user/password)</p>
  </body>
</html>
"""


def publish_message(message: str) -> None:
    credentials = pika.PlainCredentials("user", "password")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost", credentials=credentials)
    )
    channel = connection.channel()
    channel.queue_declare(queue="task_queue", durable=True)
    channel.basic_publish(
        exchange="",
        routing_key="task_queue",
        body=message,
        properties=pika.BasicProperties(delivery_mode=2),
    )
    connection.close()


@app.route("/", methods=["GET"])
def index():
    init_db()
    rows = list(fetch_recent(50))
    return render_template_string(HTML, rows=rows)


@app.route("/publish", methods=["POST"])
def publish():
    message = (request.form.get("message") or "").strip()
    if message:
        publish_message(message)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)


