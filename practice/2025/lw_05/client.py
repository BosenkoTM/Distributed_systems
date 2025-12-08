import requests
from cryptography.fernet import Fernet

def make_request():
    # Load encryption key (same as server uses)
    try:
        key = open('encryption_key.txt', 'rb').read()
        cipher = Fernet(key)
        # Encrypt the data
        plaintext_data = "Hello, this is encrypted data!"
        encrypted_data = cipher.encrypt(plaintext_data.encode()).decode()
    except FileNotFoundError:
        print("Error: encryption_key.txt not found. Please generate it first.")
        return
    
    data = {
        "certificate": open('client_cert.pem', 'r').read(),
        "data": encrypted_data
    }

    # Note: Coordinator runs on HTTP (port 8000), so we don't need SSL for coordinator connection
    # SSL/TLS is used between coordinator and backend servers
    try:
        # Make the HTTP request to coordinator
        response = requests.post('http://localhost:8000/api/data', json=data)

        if response.status_code == 200:
            print(f"[Client1] Success: {response.json()}")
        else:
            print(f"[Client1] Error: {response.status_code} - {response.text}")

    except requests.exceptions.SSLError as ssl_error:
        print(f"[Client1] SSL error: {ssl_error}")
    except requests.exceptions.RequestException as req_error:
        print(f"[Client1] Request error: {req_error}")

if __name__ == '__main__':
    make_request()