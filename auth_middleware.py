import os
import json
import firebase_admin
from firebase_admin import credentials, auth
from flask import request, jsonify
from functools import wraps

# Usa JSON da env ou ADC (produção)
cred_json = os.getenv('FIREBASE_CREDENTIALS_JSON')
if cred_json:
    cred = credentials.Certificate(json.loads(cred_json))
else:
    cred = credentials.ApplicationDefault()

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

def verificar_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token ausente'}), 401
        try:
            token = auth_header.split('Bearer ')[1]
            decoded = auth.verify_id_token(token)
            request.uid = decoded['uid']
            return func(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Token inválido ou expirado'}), 401
    return wrapper
