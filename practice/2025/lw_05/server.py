from flask import Flask, request, g
import ssl
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet

app = Flask(__name__)

@app.before_request
def verify_client_cert():
    try:
        cert = request.get_json().get('certificate')
        if not cert:
            return {'error': 'Certificate not provided'}, 401
        # Verify certificate against CA
        if not verify_certificate(cert):
            return {'error': 'Invalid certificate'}, 401
    except Exception as e:
        return {'error': f'Certificate verification error: {str(e)}'}, 401

@app.route('/api/data', methods=['POST'])
def get_data():
    try:
        data = request.get_json().get('data')
        if not data:
            return {'error': 'Data not provided'}, 400
        # Decrypt data
        decrypted_data = decrypt_data(data)
        # Process decrypted data
        print(f"Decrypted data: {decrypted_data.decode()}")
        return {'result': 'ok'}
    except Exception as e:
        return {'error': str(e)}, 400

def verify_certificate(cert_pem):
    """
    Verify that the client certificate is signed by the CA.
    In a real mTLS setup, SSL context handles this automatically,
    but here we do application-level verification.
    """
    try:
        # Load client certificate
        client_cert = load_pem_x509_certificate(cert_pem.encode(), default_backend())
        
        # Load CA certificate
        with open('ca_cert.pem', 'rb') as f:
            ca_cert = load_pem_x509_certificate(f.read(), default_backend())
        
        # Verify that client certificate is signed by CA
        ca_public_key = ca_cert.public_key()
        ca_public_key.verify(
            client_cert.signature,
            client_cert.tbs_certificate_bytes,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    except Exception as e:
        print(f"Certificate verification failed: {e}")
        return False

def decrypt_data(encrypted_data):
    """
    Decrypt data using Fernet symmetric encryption.
    """
    try:
        # Load encryption key
        with open('encryption_key.txt', 'rb') as f:
            key = f.read()
        # Decrypt data
        cipher = Fernet(key)
        # encrypted_data is a string, convert to bytes
        decrypted_bytes = cipher.decrypt(encrypted_data.encode())
        return decrypted_bytes
    except FileNotFoundError:
        raise Exception("Encryption key file not found")
    except Exception as e:
        raise Exception(f"Decryption failed: {str(e)}")

if __name__ == '__main__':
    import sys
    
    # Allow port to be specified as command line argument or environment variable
    port = 5000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    elif 'PORT' in os.environ:
        port = int(os.environ['PORT'])
    
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain('server_cert.pem', 'server_key.pem')
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_verify_locations('ca_cert.pem')
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, ssl_context=context)