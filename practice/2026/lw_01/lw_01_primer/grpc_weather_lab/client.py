import grpc

# Импортируем сгенерированные классы
import weather_pb2
import weather_pb2_grpc

def run():
    # Устанавливаем соединение с сервером
    with grpc.insecure_channel('localhost:50051') as channel:
        # Создаем "заглушку" (stub) для вызова удаленных методов
        stub = weather_pb2_grpc.WeatherServiceStub(channel)

        city_name = "Москва"
        
        # --- Вызов Unary RPC метода ---
        print(f"--- Запрос текущей погоды для города {city_name} ---")
        request = weather_pb2.CityRequest(name=city_name)
        try:
            response = stub.GetCurrentWeather(request)
            print(f"Ответ сервера: Температура {response.temperature}°C, {response.description} ({response.timestamp})")
        except grpc.RpcError as e:
            print(f"Ошибка RPC: {e.status()}: {e.details()}")

        print("\n" + "="*40 + "\n")
        
        # --- Вызов Server streaming RPC метода ---
        print(f"--- Подписка на прогноз погоды для города {city_name} ---")
        request = weather_pb2.CityRequest(name=city_name)
        try:
            # Итерируемся по потоку ответов от сервера
            forecast_stream = stub.SubscribeToForecasts(request)
            for forecast in forecast_stream:
                print(f"Получен прогноз: Температура {forecast.temperature}°C, {forecast.description} ({forecast.timestamp})")
        except grpc.RpcError as e:
            print(f"Ошибка RPC: {e.status()}: {e.details()}")

if __name__ == '__main__':
    run()
