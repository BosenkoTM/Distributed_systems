import requests

def make_request():
    data = {
        "certificate": "dummy_data_for_http",  # Можно удалить или заменить
        "data": "some_data"
    }

    s = requests.Session()
    # URL с использованием HTTP
    url = 'http://localhost:8000/api/data'

    try:
        # Отправляем запрос по HTTP без SSL-параметров
        response = s.post(url, json=data)

        if response.status_code == 200:
            print(response.json())
        else:
            print(f"Ошибка: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as req_error:
        print(f"Ошибка запроса: {req_error}")

if __name__ == '__main__':
    make_request()