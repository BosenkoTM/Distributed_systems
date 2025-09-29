#!/usr/bin/env python3
"""
Скрипт для запуска эксперимента федеративного обучения
"""

import os
import time
import requests
import json
import subprocess
import sys
from datetime import datetime

def check_docker():
    """Проверяет наличие Docker и Docker Compose"""
    try:
        subprocess.run(['docker', '--version'], check=True, capture_output=True)
        subprocess.run(['docker-compose', '--version'], check=True, capture_output=True)
        print("✓ Docker и Docker Compose установлены")
        return True
    except subprocess.CalledProcessError:
        print("✗ Docker или Docker Compose не установлены")
        return False

def create_directories():
    """Создает необходимые директории"""
    directories = ['shared', 'results', 'data']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Директория {directory} создана")

def start_services():
    """Запускает Docker сервисы"""
    print("Запуск Docker сервисов...")
    try:
        subprocess.run(['docker-compose', 'up', '-d', '--build'], check=True)
        print("✓ Сервисы запущены")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Ошибка запуска сервисов: {e}")
        return False

def wait_for_server(max_wait=300):
    """Ожидает готовности сервера"""
    print("Ожидание готовности сервера...")
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get('http://localhost:8000/status', timeout=5)
            if response.status_code == 200:
                status = response.json()
                if status['status'] == 'running':
                    print("✓ Сервер готов")
                    return True
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(5)
        print(".", end="", flush=True)
    
    print("\n✗ Таймаут ожидания сервера")
    return False

def start_training():
    """Запускает процесс обучения"""
    print("Запуск федеративного обучения...")
    try:
        response = requests.post('http://localhost:8000/start_training', timeout=30)
        if response.status_code == 200:
            print("✓ Обучение запущено")
            return True
        else:
            print(f"✗ Ошибка запуска обучения: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Ошибка соединения: {e}")
        return False

def monitor_training(max_rounds=10):
    """Мониторит процесс обучения"""
    print("Мониторинг процесса обучения...")
    
    for round_num in range(1, max_rounds + 1):
        print(f"Раунд {round_num}/{max_rounds}...")
        
        # Ждем завершения раунда
        time.sleep(30)
        
        # Проверяем статус
        try:
            response = requests.get('http://localhost:8000/status', timeout=10)
            if response.status_code == 200:
                status = response.json()
                print(f"  Текущий раунд: {status.get('current_round', 'N/A')}")
                print(f"  Клиентов получено: {status.get('clients_received', 'N/A')}")
        except requests.exceptions.RequestException:
            pass
    
    print("✓ Мониторинг завершен")

def check_results():
    """Проверяет результаты обучения"""
    print("Проверка результатов...")
    
    results_dir = 'results'
    if not os.path.exists(results_dir):
        print("✗ Директория результатов не найдена")
        return False
    
    # Проверяем наличие файлов результатов
    expected_files = ['federated_vs_centralized.png', 'training_results.json']
    
    for file in expected_files:
        file_path = os.path.join(results_dir, file)
        if os.path.exists(file_path):
            print(f"✓ {file} найден")
        else:
            print(f"✗ {file} не найден")
    
    # Показываем метрики
    json_path = os.path.join(results_dir, 'training_results.json')
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r') as f:
                results = json.load(f)
            
            print("\nРезультаты обучения:")
            print(f"  Количество раундов: {results.get('num_rounds', 'N/A')}")
            print(f"  Количество клиентов: {results.get('num_clients', 'N/A')}")
            
            fed_acc = results.get('federated_accuracy', [])
            cen_acc = results.get('centralized_accuracy', [])
            
            if fed_acc and cen_acc:
                print(f"  Финальная точность (федеративная): {fed_acc[-1]:.2f}%")
                print(f"  Финальная точность (централизованная): {cen_acc[-1]:.2f}%")
            
        except json.JSONDecodeError:
            print("✗ Ошибка чтения JSON файла")
    
    return True

def show_logs():
    """Показывает логи сервисов"""
    print("\nЛоги сервера:")
    try:
        subprocess.run(['docker-compose', 'logs', '--tail=20', 'federated-server'])
    except subprocess.CalledProcessError:
        pass
    
    print("\nЛоги клиентов:")
    try:
        subprocess.run(['docker-compose', 'logs', '--tail=10', 'client-1'])
    except subprocess.CalledProcessError:
        pass

def cleanup():
    """Очищает ресурсы"""
    print("Остановка сервисов...")
    try:
        subprocess.run(['docker-compose', 'down'], check=True)
        print("✓ Сервисы остановлены")
    except subprocess.CalledProcessError:
        print("✗ Ошибка остановки сервисов")

def main():
    """Основная функция"""
    print("=" * 60)
    print("Эксперимент федеративного обучения на CIFAR-10")
    print("=" * 60)
    
    # Проверка зависимостей
    if not check_docker():
        sys.exit(1)
    
    # Создание директорий
    create_directories()
    
    try:
        # Запуск сервисов
        if not start_services():
            sys.exit(1)
        
        # Ожидание сервера
        if not wait_for_server():
            sys.exit(1)
        
        # Запуск обучения
        if not start_training():
            sys.exit(1)
        
        # Мониторинг
        monitor_training(max_rounds=10)
        
        # Проверка результатов
        check_results()
        
        print("\n" + "=" * 60)
        print("Эксперимент завершен успешно!")
        print("Результаты сохранены в директории 'results/'")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\nЭксперимент прерван пользователем")
    except Exception as e:
        print(f"\nОшибка: {e}")
        show_logs()
    finally:
        # Очистка
        cleanup()

if __name__ == '__main__':
    main()
