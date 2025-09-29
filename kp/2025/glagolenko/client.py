#!/usr/bin/env python3
"""
Клиентская часть для федеративного обучения
Локальный агент, который обучает модель на своих данных
"""

import os
import time
import logging
import requests
import torch
import torch.nn as nn
import torch.optim as optim
from typing import Dict, Any
from models.cnn_model import CIFAR10CNN
from federated_learning.fedavg import ModelSerializer
from utils.data_utils import get_cifar10_data, split_data_for_clients, get_data_loaders, calculate_accuracy, calculate_loss
import json

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FederatedClient:
    """Клиент для федеративного обучения"""
    
    def __init__(self, client_id: int, server_url: str, device='cpu'):
        self.client_id = client_id
        self.server_url = server_url
        self.device = device
        
        # Инициализация модели
        self.local_model = CIFAR10CNN().to(device)
        
        # Загрузка и разделение данных
        self.train_dataset, self.test_dataset = get_cifar10_data()
        client_datasets = split_data_for_clients(self.train_dataset, num_clients=5, seed=42)
        self.client_dataset = client_datasets[client_id - 1]  # client_id начинается с 1
        
        # Создание загрузчиков данных
        self.train_loader, self.test_loader = get_data_loaders(
            self.client_dataset, batch_size=32, test_dataset=self.test_dataset
        )
        
        # Настройка оптимизатора и функции потерь
        self.optimizer = optim.Adam(self.local_model.parameters(), lr=0.001)
        self.criterion = nn.CrossEntropyLoss()
        
        logger.info(f"Клиент {client_id} инициализирован с {len(self.client_dataset)} образцами")
    
    def get_global_model(self) -> bool:
        """Получает глобальную модель с сервера"""
        try:
            response = requests.get(f"{self.server_url}/get_model", timeout=30)
            if response.status_code == 200:
                data = response.json()
                model_dict = data['model']
                current_round = data['round']
                
                # Загружаем параметры в локальную модель
                ModelSerializer.dict_to_model(model_dict, self.local_model)
                
                logger.info(f"Клиент {self.client_id}: Получена глобальная модель (раунд {current_round})")
                return True
            else:
                logger.error(f"Ошибка получения модели: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка соединения с сервером: {e}")
            return False
    
    def train_local_model(self, epochs=3):
        """Обучает локальную модель на своих данных"""
        self.local_model.train()
        
        for epoch in range(epochs):
            total_loss = 0.0
            correct = 0
            total = 0
            
            for batch_idx, (data, target) in enumerate(self.train_loader):
                data, target = data.to(self.device), target.to(self.device)
                
                # Обнуляем градиенты
                self.optimizer.zero_grad()
                
                # Прямой проход
                output = self.local_model(data)
                loss = self.criterion(output, target)
                
                # Обратный проход
                loss.backward()
                self.optimizer.step()
                
                # Статистика
                total_loss += loss.item()
                _, predicted = torch.max(output.data, 1)
                total += target.size(0)
                correct += (predicted == target).sum().item()
            
            # Логирование прогресса
            avg_loss = total_loss / len(self.train_loader)
            accuracy = 100 * correct / total
            
            logger.info(f"Клиент {self.client_id}, Эпоха {epoch + 1}: "
                       f"Потери = {avg_loss:.4f}, Точность = {accuracy:.2f}%")
    
    def evaluate_local_model(self):
        """Оценивает локальную модель на тестовых данных"""
        accuracy = calculate_accuracy(self.local_model, self.test_loader, self.device)
        loss = calculate_loss(self.local_model, self.test_loader, self.criterion, self.device)
        
        logger.info(f"Клиент {self.client_id}: Точность = {accuracy:.2f}%, Потери = {loss:.4f}")
        return accuracy, loss
    
    def send_model_update(self) -> bool:
        """Отправляет обновления модели на сервер"""
        try:
            # Получаем параметры модели
            model_dict = ModelSerializer.model_to_dict(self.local_model)
            num_samples = len(self.client_dataset)
            
            # Отправляем на сервер
            payload = {
                'client_id': self.client_id,
                'model_params': model_dict,
                'num_samples': num_samples
            }
            
            response = requests.post(
                f"{self.server_url}/send_update",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"Клиент {self.client_id}: Обновления отправлены на сервер")
                return True
            else:
                logger.error(f"Ошибка отправки обновлений: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка соединения с сервером: {e}")
            return False
    
    def wait_for_server_ready(self, max_wait=300):
        """Ожидает готовности сервера"""
        logger.info(f"Клиент {self.client_id}: Ожидание готовности сервера...")
        
        start_time = time.time()
        while time.time() - start_time < max_wait:
            try:
                response = requests.get(f"{self.server_url}/status", timeout=10)
                if response.status_code == 200:
                    status = response.json()
                    if status['status'] == 'running':
                        logger.info(f"Клиент {self.client_id}: Сервер готов")
                        return True
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(5)
        
        logger.error(f"Клиент {self.client_id}: Таймаут ожидания сервера")
        return False
    
    def run_federated_training(self, max_rounds=10):
        """Запускает процесс федеративного обучения"""
        logger.info(f"Клиент {self.client_id}: Начинаем федеративное обучение")
        
        # Ждем готовности сервера
        if not self.wait_for_server_ready():
            return
        
        round_count = 0
        while round_count < max_rounds:
            try:
                # Получаем глобальную модель
                if not self.get_global_model():
                    logger.error(f"Клиент {self.client_id}: Не удалось получить глобальную модель")
                    time.sleep(10)
                    continue
                
                # Обучаем локальную модель
                self.train_local_model(epochs=3)
                
                # Оцениваем локальную модель
                self.evaluate_local_model()
                
                # Отправляем обновления
                if not self.send_model_update():
                    logger.error(f"Клиент {self.client_id}: Не удалось отправить обновления")
                    time.sleep(10)
                    continue
                
                round_count += 1
                logger.info(f"Клиент {self.client_id}: Раунд {round_count} завершен")
                
                # Ждем перед следующим раундом
                time.sleep(5)
                
            except KeyboardInterrupt:
                logger.info(f"Клиент {self.client_id}: Обучение прервано пользователем")
                break
            except Exception as e:
                logger.error(f"Клиент {self.client_id}: Ошибка в раунде {round_count + 1}: {e}")
                time.sleep(10)
        
        logger.info(f"Клиент {self.client_id}: Федеративное обучение завершено")


def main():
    """Основная функция клиента"""
    # Получаем параметры из переменных окружения
    client_id = int(os.environ.get('CLIENT_ID', 1))
    server_url = os.environ.get('SERVER_URL', 'http://localhost:8000')
    
    # Определяем устройство
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    logger.info(f"Клиент {client_id}: Используется устройство: {device}")
    
    # Создаем и запускаем клиента
    client = FederatedClient(client_id, server_url, device)
    client.run_federated_training(max_rounds=10)

if __name__ == '__main__':
    main()
