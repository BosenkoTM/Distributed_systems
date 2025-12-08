#!/usr/bin/env python3
"""
Скрипт для генерации ключа шифрования Fernet.
Этот ключ используется для симметричного шифрования данных между клиентом и сервером.
"""

from cryptography.fernet import Fernet

def generate_encryption_key():
    """Генерирует ключ шифрования Fernet и сохраняет его в файл."""
    key = Fernet.generate_key()
    with open('encryption_key.txt', 'wb') as f:
        f.write(key)
    print("✓ Ключ шифрования успешно сгенерирован и сохранен в encryption_key.txt")
    print(f"  Длина ключа: {len(key)} байт")
    return key

if __name__ == '__main__':
    generate_encryption_key()

