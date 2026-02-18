import grpc
from concurrent import futures
import time
import random

# Импортируем сгенерированные классы
import weather_pb2
import weather_pb2_grpc

# Класс WeatherServiceServicer реализует логику нашего сервиса
class WeatherServiceServicer(weather_pb2_grpc.WeatherServiceServicer):

    # Реализация Unary RPC метода
    def GetCurrentWeather(self, request, context):
        print(f"Получен запрос для города: {request.name}")
        # Имитируем получение данных о погоде
        temperature = round(random.uniform(-10.0, 30.0), 1)
        description = random.choice(["Солнечно", "Облачно", "Дождь", "Снег"])
        
        return weather_pb2.WeatherResponse(
            temperature=temperature,
            description=description,
            timestamp=time.ctime()
        )

    # Реализация Server streaming RPC метода
    def SubscribeToForecasts(self, request, context):
        print(f"Получен запрос на подписку для города: {request.name}")
        # Имитируем отправку прогноза каждые 2 секунды
        for i in range(5): # Отправим 5 прогнозов
            temperature = round(random.uniform(-5.0, 25.0), 1)
            description = random.choice(["Ясно", "Переменная облачность", "Небольшой дождь"])
            
            # Создаем и отправляем ответное сообщение
            response = weather_pb2.WeatherResponse(
                temperature=temperature,
                description=f"Прогноз на {i+1} день",
                timestamp=time.ctime()
            )
            yield response
            time.sleep(2) # Пауза между отправками

def serve():
    # Создаем сервер с 10 рабочими потоками
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # Регистрируем наш сервис на сервере
    weather_pb2_grpc.add_WeatherServiceServicer_to_server(
        WeatherServiceServicer(), server
    )
    # Запускаем сервер на порту 50051
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Сервер запущен на порту 50051...")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
