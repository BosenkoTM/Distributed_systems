import grpc
from concurrent import futures
import message_service_pb2
import message_service_pb2_grpc


class MessageService(message_service_pb2_grpc.MessageServiceServicer):
    def AssignAB(self, request, context):
        user_id = request.user_id or ""
        bucket = (sum(user_id.encode("utf-8")) % 2) if user_id else 0
        group = "A" if bucket == 0 else "B"
        print(f"[AssignAB] user_id={user_id!r} -> group={group}")
        return message_service_pb2.ABResponse(group=group)

    def Factorial(self, request, context):
        n = int(request.n)
        if n < 0:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "n must be non-negative")
        result = 1
        for i in range(2, n + 1):
            result *= i
        print(f"[Factorial] n={n} -> value={result}")
        return message_service_pb2.FactorialResponse(value=str(result))

    def MostFrequentLetter(self, request, context):
        text = request.text or ""
        frequency_by_letter = {}
        for ch in text.lower():
            if ch.isalpha():
                frequency_by_letter[ch] = frequency_by_letter.get(ch, 0) + 1
        if not frequency_by_letter:
            print("[MostFrequentLetter] empty/none alpha -> letter=''")
            return message_service_pb2.LetterResponse(letter="")
        letter = sorted(
            frequency_by_letter.items(), key=lambda kv: (-kv[1], kv[0])
        )[0][0]
        print(f"[MostFrequentLetter] text_len={len(text)} -> letter={letter}")
        return message_service_pb2.LetterResponse(letter=letter)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    message_service_pb2_grpc.add_MessageServiceServicer_to_server(
        MessageService(), server
    )
    server.add_insecure_port("[::]:50051")
    print("gRPC server running on 50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()


