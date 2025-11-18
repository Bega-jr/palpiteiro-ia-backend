from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import requests
from firebase_admin import credentials, firestore, initialize_app, auth as fb_auth

app = Flask(__name__)
CORS(app)

# CAMINHO 100% CONFIRMADO DO RENDER EM NOVEMBRO 2025
cred = credentials.Certificate("/etc/secrets/firebase-adminsdk.json")
initialize_app(cred)
db = firestore.client()

@app.route('/')
def home():
    return jsonify({"status": "VERDE FINAL", "message": "Palpiteiro IA v2 – FUNCIONANDO 100%!"})

@app.route('/historico')
def historico():
    try:
        r = requests.get('https://api.guidi.dev.br/loteria/lotofacil/ultimo', timeout=8)
        return jsonify(r.json())
    except:
        return jsonify({"sorteios": []})

@app.route('/gerar_palpites')
def gerar_palpites():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return jsonify({"error": "token missing"}), 401
    try:
        decoded = fb_auth.verify_id_token(token)
        uid = decoded['uid']
    except:
        return jsonify({"error": "token inválido"}), 401

    numeros = sorted(random.sample(range(1, 26), 15))
    db.collection('usuarios').document(uid).collection('apostas').add({
        'numeros': numeros,
        'timestamp': firestore.SERVER_TIMESTAMP
    })
    return jsonify({"palpites": [numeros]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
