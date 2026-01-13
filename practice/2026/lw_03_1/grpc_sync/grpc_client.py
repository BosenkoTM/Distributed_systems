import os
import grpc
import message_service_pb2
import message_service_pb2_grpc


GRPC_TARGET = os.getenv("GRPC_TARGET", "127.0.0.1:50051")


def run():
    with grpc.insecure_channel(GRPC_TARGET) as channel:
        stub = message_service_pb2_grpc.MessageServiceStub(channel)
        print("AssignAB:", stub.AssignAB(message_service_pb2.ABRequest(user_id="user42")).group)
        print(
            "Factorial:",
            stub.Factorial(message_service_pb2.FactorialRequest(n=6)).value,
        )
        print(
            "MostFrequentLetter:",
            stub.MostFrequentLetter(
                message_service_pb2.TextRequest(text="abracadabra")
            ).letter,
        )


if __name__ == "__main__":
    run()


