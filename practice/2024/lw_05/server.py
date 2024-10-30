from flask import Flask, request, g
import ssl
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet

app = Flask(__name__)

@app.before_request
def verify_client_cert():
    cert = request.get_json()['certificate']
    # Verify certificate against CA
    if not verify_certificate(cert):
        return "Invalid certificate", 401

@app.route('/api/data', methods=['POST'])
def get_data():
    data = request.get_json()['data']
    # Decrypt data
    decrypted_data = decrypt_data(data)
    # Process decrypted data
    return {'result': 'ok'}

def verify_certificate(cert_pem):
    # Load certificate
    certificate = load_pem_x509_certificate(cert_pem.encode(), default_backend())
    # Verify certificate against CA
    try:
        certificate.public_key().verify(
            certificate.signature,
            certificate.tbs_certificate_bytes,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    except:
        return False

def decrypt_data(encrypted_data):
    # Load encryption key
    key = open('encryption_key.txt', 'rb').read()
    # Decrypt data
    cipher = Fernet(key)
    return cipher.decrypt(encrypted_data.encode())

if __name__ == '__main__':
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain('server_cert.pem', 'server_key.pem')
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_verify_locations('ca_cert.pem')
    app.run(host='0.0.0.0', port=5000, ssl_context=context)