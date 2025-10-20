import os
import sys
import time
import pika
import grpc


# Ensure we can import generated gRPC modules from sibling directory
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(repo_root, "grpc_sync"))

import message_service_pb2  # noqa: E402
import message_service_pb2_grpc  # noqa: E402
from storage import init_db, insert_result


GRPC_TARGET = os.getenv("GRPC_TARGET", "127.0.0.1:50051")


def process_via_grpc(text: str) -> str:
    # Несколько попыток на случай, если gRPC сервер ещё не поднялся
    last_error = None
    backoffs = [0.5, 1.0, 2.0]
    for delay in backoffs:
        try:
            with grpc.insecure_channel(GRPC_TARGET) as channel:
                stub = message_service_pb2_grpc.MessageServiceStub(channel)
                if text.startswith("fact:"):
                    n = int(text.split(":", 1)[1])
                    return stub.Factorial(message_service_pb2.FactorialRequest(n=n)).value
                if text.startswith("freq:"):
                    payload = text.split(":", 1)[1]
                    return stub.MostFrequentLetter(
                        message_service_pb2.TextRequest(text=payload)
                    ).letter
                return stub.AssignAB(message_service_pb2.ABRequest(user_id=text)).group
        except grpc.RpcError as exc:
            last_error = exc
            time.sleep(delay)
    return f"gRPC error: {getattr(last_error, 'details', lambda: str(last_error))()}"


def wait_for_grpc_ready(total_timeout_seconds: float = 30.0) -> bool:
    end = time.time() + total_timeout_seconds
    while time.time() < end:
        try:
            channel = grpc.insecure_channel(GRPC_TARGET)
            grpc.channel_ready_future(channel).result(timeout=2.0)
            return True
        except Exception:
            time.sleep(1.0)
    return False


def main():
    init_db()
    credentials = pika.PlainCredentials("user", "password")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost", credentials=credentials)
    )
    channel = connection.channel()
    channel.queue_declare(queue="task_queue", durable=True)
    print(" [*] Waiting for messages. To exit press CTRL+C")

    if not wait_for_grpc_ready():
        print(f" [!] gRPC server is not reachable on {GRPC_TARGET} after 30s; will still consume and retry per-message")

    def callback(ch, method, properties, body):
        raw = body.decode()
        print(f" [x] Received: {raw}")
        # Поддержка батч‑строки вида "user42, fact:6, freq:abracadabra"
        parts = [p.strip() for p in raw.split(',') if p.strip()]
        if not parts:
            parts = [raw.strip()]
        for text in parts:
            result = process_via_grpc(text)
            method_name = (
                "Factorial"
                if text.startswith("fact:")
                else ("MostFrequentLetter" if text.startswith("freq:") else "AssignAB")
            )
            insert_result(text, method_name, result)
            print(f" [✓] {method_name} {text!r} -> {result}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue="task_queue", on_message_callback=callback)
    channel.start_consuming()


if __name__ == "__main__":
    main()


