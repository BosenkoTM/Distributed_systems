import torch
import numpy as np
from typing import List, Dict, Any


class FedAvg:
    """
    Реализация алгоритма Federated Averaging (FedAvg)
    """
    
    def __init__(self):
        self.client_weights = []
        self.client_sizes = []
    
    def add_client_update(self, model_parameters: List[torch.Tensor], num_samples: int):
        """
        Добавляет обновления от клиента
        
        Args:
            model_parameters: Параметры модели от клиента
            num_samples: Количество образцов, использованных для обучения
        """
        self.client_weights.append(model_parameters)
        self.client_sizes.append(num_samples)
    
    def aggregate(self) -> List[torch.Tensor]:
        """
        Агрегирует обновления от всех клиентов используя FedAvg
        
        Returns:
            List[torch.Tensor]: Агрегированные параметры модели
        """
        if not self.client_weights:
            raise ValueError("Нет обновлений от клиентов для агрегации")
        
        # Вычисляем общее количество образцов
        total_samples = sum(self.client_sizes)
        
        # Инициализируем агрегированные параметры
        aggregated_params = []
        num_layers = len(self.client_weights[0])
        
        for layer_idx in range(num_layers):
            # Инициализируем с нулевыми тензорами того же размера
            aggregated_layer = torch.zeros_like(self.client_weights[0][layer_idx])
            
            # Взвешенное суммирование параметров
            for client_idx, client_params in enumerate(self.client_weights):
                weight = self.client_sizes[client_idx] / total_samples
                aggregated_layer += weight * client_params[layer_idx]
            
            aggregated_params.append(aggregated_layer)
        
        return aggregated_params
    
    def reset(self):
        """Сбрасывает накопленные обновления"""
        self.client_weights = []
        self.client_sizes = []
    
    def get_client_count(self) -> int:
        """Возвращает количество клиентов, отправивших обновления"""
        return len(self.client_weights)


class ModelSerializer:
    """
    Утилиты для сериализации и десериализации моделей
    """
    
    @staticmethod
    def model_to_dict(model: torch.nn.Module) -> Dict[str, Any]:
        """
        Конвертирует модель в словарь для передачи
        
        Args:
            model: PyTorch модель
        
        Returns:
            Dict: Словарь с параметрами модели
        """
        model_dict = {}
        for name, param in model.named_parameters():
            model_dict[name] = param.data.cpu().numpy()
        return model_dict
    
    @staticmethod
    def dict_to_model(model_dict: Dict[str, Any], model: torch.nn.Module):
        """
        Загружает параметры из словаря в модель
        
        Args:
            model_dict: Словарь с параметрами
            model: Модель для загрузки параметров
        """
        for name, param in model.named_parameters():
            if name in model_dict:
                param.data = torch.from_numpy(model_dict[name]).to(param.device)
    
    @staticmethod
    def parameters_to_list(model: torch.nn.Module) -> List[torch.Tensor]:
        """
        Извлекает параметры модели как список тензоров
        
        Args:
            model: PyTorch модель
        
        Returns:
            List[torch.Tensor]: Список параметров
        """
        return [param.data.clone() for param in model.parameters()]
    
    @staticmethod
    def list_to_parameters(parameters: List[torch.Tensor], model: torch.nn.Module):
        """
        Загружает параметры из списка в модель
        
        Args:
            parameters: Список параметров
            model: Модель для загрузки
        """
        for param, new_param in zip(model.parameters(), parameters):
            param.data.copy_(new_param)
