from flask import Flask, request
import requests

app = Flask(__name__)
# Note: For local testing, use different ports for multiple servers
# For production, use different IP addresses or domain names
server_urls = ['https://127.0.0.1:5001', 'https://127.0.0.1:5002']

@app.route('/api/data', methods=['POST'])
def handle_request():
    data = request.get_json()
    for url in server_urls:
        try:
            # Coordinator needs to provide client certificate for mTLS
            # Verify server certificates using CA certificate
            response = requests.post(
                f"{url}/api/data", 
                json=data, 
                verify='ca_cert.pem',
                cert=('client_cert.pem', 'client_key.pem'),  # Client certificate for mTLS
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Server {url} failed: {e}")
            continue
    return {'error': 'All servers are down'}, 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)