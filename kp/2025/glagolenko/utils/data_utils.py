import torch
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader, Subset
import numpy as np
from sklearn.model_selection import train_test_split


def get_cifar10_data():
    """
    Загружает и подготавливает данные CIFAR-10
    """
    # Трансформации для обучения
    transform_train = transforms.Compose([
        transforms.RandomCrop(32, padding=4),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
    ])
    
    # Трансформации для тестирования
    transform_test = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
    ])
    
    # Загрузка тренировочного набора
    train_dataset = torchvision.datasets.CIFAR10(
        root='./data', train=True, download=True, transform=transform_train
    )
    
    # Загрузка тестового набора
    test_dataset = torchvision.datasets.CIFAR10(
        root='./data', train=False, download=True, transform=transform_test
    )
    
    return train_dataset, test_dataset


def split_data_for_clients(train_dataset, num_clients=5, seed=42):
    """
    Разделяет данные между клиентами для симуляции федеративного обучения
    
    Args:
        train_dataset: Тренировочный датасет
        num_clients: Количество клиентов
        seed: Случайное зерно для воспроизводимости
    
    Returns:
        List[Subset]: Список подмножеств данных для каждого клиента
    """
    np.random.seed(seed)
    
    # Получаем индексы всех данных
    total_size = len(train_dataset)
    indices = np.arange(total_size)
    
    # Разделяем данные на непересекающиеся части
    # Используем стратифицированное разделение для равномерного распределения классов
    labels = [train_dataset[i][1] for i in indices]
    
    # Разделяем данные на части
    client_indices = []
    remaining_indices = indices.copy()
    remaining_labels = labels.copy()
    
    for i in range(num_clients - 1):
        # Вычисляем размер части для текущего клиента
        remaining_clients = num_clients - i
        client_size = len(remaining_indices) // remaining_clients
        
        # Стратифицированное разделение
        client_idx, remaining_indices, _, remaining_labels = train_test_split(
            remaining_indices, remaining_labels, 
            train_size=client_size, 
            stratify=remaining_labels,
            random_state=seed + i
        )
        client_indices.append(client_idx)
    
    # Последний клиент получает оставшиеся данные
    client_indices.append(remaining_indices)
    
    # Создаем подмножества для каждого клиента
    client_datasets = []
    for indices in client_indices:
        client_datasets.append(Subset(train_dataset, indices))
    
    return client_datasets


def get_data_loaders(client_dataset, batch_size=32, test_dataset=None):
    """
    Создает DataLoader для клиента
    
    Args:
        client_dataset: Датасет клиента
        batch_size: Размер батча
        test_dataset: Тестовый датасет (опционально)
    
    Returns:
        Tuple[DataLoader, DataLoader]: Тренировочный и тестовый загрузчики
    """
    train_loader = DataLoader(
        client_dataset, batch_size=batch_size, shuffle=True, num_workers=2
    )
    
    test_loader = None
    if test_dataset is not None:
        test_loader = DataLoader(
            test_dataset, batch_size=batch_size, shuffle=False, num_workers=2
        )
    
    return train_loader, test_loader


def calculate_accuracy(model, data_loader, device):
    """
    Вычисляет точность модели на данных
    
    Args:
        model: Модель для тестирования
        data_loader: Загрузчик данных
        device: Устройство для вычислений
    
    Returns:
        float: Точность модели
    """
    model.eval()
    correct = 0
    total = 0
    
    with torch.no_grad():
        for data, target in data_loader:
            data, target = data.to(device), target.to(device)
            outputs = model(data)
            _, predicted = torch.max(outputs.data, 1)
            total += target.size(0)
            correct += (predicted == target).sum().item()
    
    return 100 * correct / total


def calculate_loss(model, data_loader, criterion, device):
    """
    Вычисляет потери модели на данных
    
    Args:
        model: Модель для тестирования
        data_loader: Загрузчик данных
        criterion: Функция потерь
        device: Устройство для вычислений
    
    Returns:
        float: Средние потери
    """
    model.eval()
    total_loss = 0.0
    total_samples = 0
    
    with torch.no_grad():
        for data, target in data_loader:
            data, target = data.to(device), target.to(device)
            outputs = model(data)
            loss = criterion(outputs, target)
            total_loss += loss.item() * data.size(0)
            total_samples += data.size(0)
    
    return total_loss / total_samples
