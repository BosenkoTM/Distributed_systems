#!/bin/bash
# Скрипт для автоматической генерации всех необходимых сертификатов и ключей
# для лабораторной работы по безопасности распределенных систем

set -e  # Остановить выполнение при ошибке

echo "=== Генерация инфраструктуры PKI для mTLS ==="
echo ""

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Генерация приватного ключа CA
echo -e "${YELLOW}[1/8]${NC} Генерация приватного ключа CA..."
openssl genrsa -out ca_key.pem 2048
echo -e "${GREEN}✓${NC} CA ключ создан: ca_key.pem"

# 2. Создание самоподписанного сертификата CA
echo -e "${YELLOW}[2/8]${NC} Создание сертификата CA..."
openssl req -new -x509 -days 365 -key ca_key.pem -out ca_cert.pem \
  -subj "/C=RU/ST=Moscow/L=Moscow/O=Lab5/OU=IT/CN=CA"
echo -e "${GREEN}✓${NC} CA сертификат создан: ca_cert.pem"

# 3. Генерация приватного ключа сервера
echo -e "${YELLOW}[3/8]${NC} Генерация приватного ключа сервера..."
openssl genrsa -out server_key.pem 2048
echo -e "${GREEN}✓${NC} Серверный ключ создан: server_key.pem"

# 4. Создание запроса на сертификат сервера (CSR)
echo -e "${YELLOW}[4/8]${NC} Создание запроса на сертификат сервера..."
openssl req -new -key server_key.pem -out server_csr.pem \
  -subj "/C=RU/ST=Moscow/L=Moscow/O=Lab5/OU=Server/CN=localhost"
echo -e "${GREEN}✓${NC} CSR сервера создан: server_csr.pem"

# 5. Подписание сертификата сервера CA с Subject Alternative Name (SAN)
echo -e "${YELLOW}[5/8]${NC} Подписание сертификата сервера CA..."
# Создаем временный конфигурационный файл для SAN
cat > server_cert_ext.conf <<EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req

[v3_req]
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
IP.1 = 127.0.0.1
IP.2 = ::1
EOF

openssl x509 -req -days 365 -in server_csr.pem -CA ca_cert.pem \
  -CAkey ca_key.pem -CAcreateserial -out server_cert.pem \
  -extensions v3_req -extfile server_cert_ext.conf
rm -f server_cert_ext.conf
echo -e "${GREEN}✓${NC} Серверный сертификат создан: server_cert.pem (с SAN для localhost и 127.0.0.1)"

# 6. Генерация приватного ключа клиента
echo -e "${YELLOW}[6/8]${NC} Генерация приватного ключа клиента..."
openssl genrsa -out client_key.pem 2048
echo -e "${GREEN}✓${NC} Клиентский ключ создан: client_key.pem"

# 7. Создание запроса на сертификат клиента (CSR)
echo -e "${YELLOW}[7/8]${NC} Создание запроса на сертификат клиента..."
openssl req -new -key client_key.pem -out client_csr.pem \
  -subj "/C=RU/ST=Moscow/L=Moscow/O=Lab5/OU=Client/CN=client"
echo -e "${GREEN}✓${NC} CSR клиента создан: client_csr.pem"

# 8. Подписание сертификата клиента CA
echo -e "${YELLOW}[8/8]${NC} Подписание сертификата клиента CA..."
openssl x509 -req -days 365 -in client_csr.pem -CA ca_cert.pem \
  -CAkey ca_key.pem -CAcreateserial -out client_cert.pem
echo -e "${GREEN}✓${NC} Клиентский сертификат создан: client_cert.pem"

# Удаление временных файлов CSR
echo ""
echo "Удаление временных файлов..."
rm -f server_csr.pem client_csr.pem
echo -e "${GREEN}✓${NC} Временные файлы удалены"

echo ""
echo -e "${GREEN}=== Генерация завершена успешно! ===${NC}"
echo ""
echo "Созданные файлы:"
echo "  - ca_key.pem (приватный ключ CA - хранить в секрете!)"
echo "  - ca_cert.pem (сертификат CA)"
echo "  - server_key.pem (приватный ключ сервера)"
echo "  - server_cert.pem (сертификат сервера)"
echo "  - client_key.pem (приватный ключ клиента)"
echo "  - client_cert.pem (сертификат клиента)"
echo ""
echo "Следующий шаг: выполните 'python3 generate_key.py' для генерации ключа шифрования"

