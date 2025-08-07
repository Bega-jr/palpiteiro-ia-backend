import firebase_admin
from firebase_admin import credentials, auth
from flask import request, jsonify

cred = credentials.Certificate('firebase-adminsdk.json')
firebase_admin.initialize_app(cred)

def verificar_token(func):
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({'error': 'Token ausente ou inválido'}), 401
        try:
            token = auth_header.split("Bearer ")[1]
            decoded = auth.verify_id_token(token)
            request.uid = decoded['uid']
        except Exception as e:
            return jsonify({'error': 'Token inválido ou expirado'}), 401
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper