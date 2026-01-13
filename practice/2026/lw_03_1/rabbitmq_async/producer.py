import pika
import sys


def main():
    credentials = pika.PlainCredentials("user", "password")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost", credentials=credentials)
    )
    channel = connection.channel()
    channel.queue_declare(queue="task_queue", durable=True)

    message = " ".join(sys.argv[1:]) or "user42"
    channel.basic_publish(
        exchange="",
        routing_key="task_queue",
        body=message,
        properties=pika.BasicProperties(delivery_mode=2),
    )
    print(f" [x] Sent: {message}")
    connection.close()


if __name__ == "__main__":
    main()


