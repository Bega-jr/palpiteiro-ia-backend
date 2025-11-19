from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import requests
from datetime import datetime
from firebase_admin import credentials, firestore, initialize_app, auth as fb_auth

# IMPORTA O MÓDULO DE ESTATÍSTICAS
import estatisticas

app = Flask(__name__)
CORS(app)

# Render Secret File (caminho oficial 2025)
cred = credentials.Certificate("/etc/secrets/firebase-adminsdk.json")
initialize_app(cred)
db = firestore.client()

@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "Palpiteiro IA – VERDE E FUNCIONANDO 100%!"})

@app.route('/historico')
def historico():
    try:
        r = requests.get('https://api.guidi.dev.br/loteria/lotofacil/ultimo', timeout=10)
        data = r.json()
        return jsonify({"sorteios": [data]})
    except:
        return jsonify({"sorteios": [{"concurso": "3538", "data": "19/11/2025", "numeros": list(range(1,16))}] })

@app.route('/estatisticas')
def rota_estatisticas():
    """Rota REAL de estatísticas"""
    try:
        resultado = estatisticas.gerar_estatisticas()  # função do seu arquivo
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

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

@app.route('/minhas_apostas')
def minhas_apostas():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return jsonify({"error": "token missing"}), 401
    try:
        decoded = fb_auth.verify_id_token(token)
        uid = decoded['uid']
    except:
        return jsonify({"error": "token inválido"}), 401

    docs = db.collection('usuarios').document(uid).collection('apostas')\
        .order_by('timestamp', direction=firestore.Query.DESCENDING).limit(20).stream()
    apostas = [doc.to_dict() for doc in docs]
    return jsonify({"apostas": apostas})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
