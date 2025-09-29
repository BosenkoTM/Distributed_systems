#!/usr/bin/env python3
"""
Серверная часть для федеративного обучения
Центральный координатор, который управляет процессом обучения
"""

import os
import json
import time
import logging
from typing import Dict, List, Any
from flask import Flask, request, jsonify
import torch
import numpy as np
from models.cnn_model import CIFAR10CNN
from federated_learning.fedavg import FedAvg, ModelSerializer
from utils.data_utils import get_cifar10_data, get_data_loaders, calculate_accuracy, calculate_loss
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class FederatedServer:
    """Сервер для координации федеративного обучения"""
    
    def __init__(self, num_clients=5, num_rounds=10, device='cpu'):
        self.num_clients = num_clients
        self.num_rounds = num_rounds
        self.device = device
        self.current_round = 0
        
        # Инициализация модели
        self.global_model = CIFAR10CNN().to(device)
        self.initial_model_state = ModelSerializer.parameters_to_list(self.global_model)
        
        # FedAvg агрегатор
        self.fedavg = FedAvg()
        
        # Загрузка данных
        self.train_dataset, self.test_dataset = get_cifar10_data()
        _, self.test_loader = get_data_loaders(None, test_dataset=self.test_dataset)
        
        # Метрики для визуализации
        self.federated_accuracy = []
        self.federated_loss = []
        self.centralized_accuracy = []
        self.centralized_loss = []
        
        # Создание директорий для результатов
        os.makedirs('/app/results', exist_ok=True)
        os.makedirs('/app/shared', exist_ok=True)
        
        logger.info(f"Сервер инициализирован с {num_clients} клиентами на {num_rounds} раундов")
    
    def get_global_model(self) -> Dict[str, Any]:
        """Возвращает текущую глобальную модель"""
        return ModelSerializer.model_to_dict(self.global_model)
    
    def receive_client_update(self, client_id: int, model_params: Dict[str, Any], num_samples: int):
        """Получает обновления от клиента"""
        # Конвертируем параметры обратно в тензоры
        temp_model = CIFAR10CNN().to(self.device)
        ModelSerializer.dict_to_model(model_params, temp_model)
        parameters = ModelSerializer.parameters_to_list(temp_model)
        
        # Добавляем в агрегатор
        self.fedavg.add_client_update(parameters, num_samples)
        
        logger.info(f"Получены обновления от клиента {client_id} ({num_samples} образцов)")
    
    def aggregate_updates(self):
        """Агрегирует обновления от всех клиентов"""
        if self.fedavg.get_client_count() == 0:
            logger.warning("Нет обновлений для агрегации")
            return
        
        # Агрегируем параметры
        aggregated_params = self.fedavg.aggregate()
        
        # Обновляем глобальную модель
        ModelSerializer.list_to_parameters(aggregated_params, self.global_model)
        
        # Сбрасываем агрегатор
        self.fedavg.reset()
        
        logger.info(f"Раунд {self.current_round}: Модель агрегирована от {self.fedavg.get_client_count()} клиентов")
    
    def evaluate_global_model(self):
        """Оценивает глобальную модель на тестовых данных"""
        criterion = torch.nn.CrossEntropyLoss()
        
        accuracy = calculate_accuracy(self.global_model, self.test_loader, self.device)
        loss = calculate_loss(self.global_model, self.test_loader, criterion, self.device)
        
        self.federated_accuracy.append(accuracy)
        self.federated_loss.append(loss)
        
        logger.info(f"Раунд {self.current_round}: Точность = {accuracy:.2f}%, Потери = {loss:.4f}")
        
        return accuracy, loss
    
    def train_centralized_model(self):
        """Обучает централизованную модель для сравнения"""
        logger.info("Начинаем обучение централизованной модели...")
        
        # Создаем копию модели
        centralized_model = CIFAR10CNN().to(self.device)
        ModelSerializer.list_to_parameters(self.initial_model_state, centralized_model)
        
        # Загружаем все данные
        train_loader, _ = get_data_loaders(self.train_dataset, batch_size=32)
        
        # Настройка оптимизатора и функции потерь
        optimizer = torch.optim.Adam(centralized_model.parameters(), lr=0.001)
        criterion = torch.nn.CrossEntropyLoss()
        
        # Обучение
        for epoch in range(self.num_rounds):
            centralized_model.train()
            total_loss = 0.0
            
            for batch_idx, (data, target) in enumerate(train_loader):
                data, target = data.to(self.device), target.to(self.device)
                
                optimizer.zero_grad()
                output = centralized_model(data)
                loss = criterion(output, target)
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            # Оценка на тестовых данных
            accuracy = calculate_accuracy(centralized_model, self.test_loader, self.device)
            avg_loss = calculate_loss(centralized_model, self.test_loader, criterion, self.device)
            
            self.centralized_accuracy.append(accuracy)
            self.centralized_loss.append(avg_loss)
            
            logger.info(f"Эпоха {epoch + 1}: Точность = {accuracy:.2f}%, Потери = {avg_loss:.4f}")
    
    def create_visualizations(self):
        """Создает графики для сравнения результатов"""
        plt.style.use('seaborn-v0_8')
        
        # График 1: Сравнение точности
        plt.figure(figsize=(12, 8))
        
        plt.subplot(2, 1, 1)
        rounds = range(1, len(self.federated_accuracy) + 1)
        plt.plot(rounds, self.federated_accuracy, 'b-o', label='Федеративная модель', linewidth=2, markersize=6)
        plt.plot(rounds, self.centralized_accuracy, 'r-s', label='Централизованная модель', linewidth=2, markersize=6)
        plt.xlabel('Раунд/Эпоха')
        plt.ylabel('Точность (%)')
        plt.title('Сравнение точности федеративной и централизованной моделей')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # График 2: Сравнение потерь
        plt.subplot(2, 1, 2)
        plt.plot(rounds, self.federated_loss, 'b-o', label='Федеративная модель', linewidth=2, markersize=6)
        plt.plot(rounds, self.centralized_loss, 'r-s', label='Централизованная модель', linewidth=2, markersize=6)
        plt.xlabel('Раунд/Эпоха')
        plt.ylabel('Функция потерь')
        plt.title('Сравнение потерь федеративной и централизованной моделей')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('/app/results/federated_vs_centralized.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Сохранение метрик в JSON
        results = {
            'federated_accuracy': self.federated_accuracy,
            'federated_loss': self.federated_loss,
            'centralized_accuracy': self.centralized_accuracy,
            'centralized_loss': self.centralized_loss,
            'num_rounds': self.num_rounds,
            'num_clients': self.num_clients,
            'timestamp': datetime.now().isoformat()
        }
        
        with open('/app/results/training_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info("Результаты сохранены в /app/results/")
    
    def run_federated_training(self):
        """Запускает процесс федеративного обучения"""
        logger.info("Начинаем федеративное обучение...")
        
        # Оценка начальной модели
        self.evaluate_global_model()
        
        # Ожидание обновлений от клиентов
        for round_num in range(1, self.num_rounds + 1):
            self.current_round = round_num
            logger.info(f"Начинаем раунд {round_num}")
            
            # Ждем обновления от всех клиентов
            start_time = time.time()
            while self.fedavg.get_client_count() < self.num_clients:
                time.sleep(1)
                if time.time() - start_time > 300:  # 5 минут таймаут
                    logger.warning(f"Таймаут ожидания клиентов в раунде {round_num}")
                    break
            
            # Агрегируем обновления
            self.aggregate_updates()
            
            # Оцениваем модель
            self.evaluate_global_model()
        
        # Обучаем централизованную модель для сравнения
        self.train_centralized_model()
        
        # Создаем визуализации
        self.create_visualizations()
        
        logger.info("Федеративное обучение завершено!")


# Глобальный экземпляр сервера
server = None

@app.route('/get_model', methods=['GET'])
def get_model():
    """API endpoint для получения глобальной модели"""
    global server
    if server is None:
        return jsonify({'error': 'Сервер не инициализирован'}), 500
    
    model_dict = server.get_global_model()
    return jsonify({
        'model': model_dict,
        'round': server.current_round
    })

@app.route('/send_update', methods=['POST'])
def send_update():
    """API endpoint для отправки обновлений от клиента"""
    global server
    if server is None:
        return jsonify({'error': 'Сервер не инициализирован'}), 500
    
    try:
        data = request.json
        client_id = data['client_id']
        model_params = data['model_params']
        num_samples = data['num_samples']
        
        server.receive_client_update(client_id, model_params, num_samples)
        
        return jsonify({'status': 'success', 'message': f'Обновления от клиента {client_id} получены'})
    
    except Exception as e:
        logger.error(f"Ошибка при получении обновлений: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/status', methods=['GET'])
def status():
    """API endpoint для проверки статуса сервера"""
    global server
    if server is None:
        return jsonify({'status': 'not_initialized'})
    
    return jsonify({
        'status': 'running',
        'current_round': server.current_round,
        'num_clients': server.num_clients,
        'num_rounds': server.num_rounds,
        'clients_received': server.fedavg.get_client_count()
    })

@app.route('/start_training', methods=['POST'])
def start_training():
    """API endpoint для запуска обучения"""
    global server
    if server is None:
        return jsonify({'error': 'Сервер не инициализирован'}), 500
    
    # Запускаем обучение в отдельном потоке
    import threading
    training_thread = threading.Thread(target=server.run_federated_training)
    training_thread.daemon = True
    training_thread.start()
    
    return jsonify({'status': 'training_started'})

def main():
    """Основная функция сервера"""
    global server
    
    # Определяем устройство
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    logger.info(f"Используется устройство: {device}")
    
    # Инициализируем сервер
    server = FederatedServer(num_clients=5, num_rounds=10, device=device)
    
    # Запускаем Flask сервер
    logger.info("Запуск Flask сервера на порту 8000...")
    app.run(host='0.0.0.0', port=8000, debug=False)

if __name__ == '__main__':
    main()
