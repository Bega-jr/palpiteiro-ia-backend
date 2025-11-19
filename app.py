from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import requests
from datetime import datetime
from firebase_admin import credentials, firestore, initialize_app, auth as fb_auth
import pandas as pd
from collections import Counter

# -----------------------------------------------------------------------------
# Inicialização do APP
# -----------------------------------------------------------------------------
app = Flask(__name__)
CORS(app)

# -----------------------------------------------------------------------------
# Firebase (Render – caminho correto dos secrets)
# -----------------------------------------------------------------------------
cred = credentials.Certificate("/etc/secrets/firebase-adminsdk.json")
initialize_app(cred)
db = firestore.client()

# -----------------------------------------------------------------------------
# Carregamento do histórico da Lotofácil
# -----------------------------------------------------------------------------
try:
    df = pd.read_csv("historico_lotofacil.csv")
    print("✔ CSV carregado com sucesso.")
except Exception as e:
    print("❌ ERRO ao carregar CSV:", e)
    df = None

# -----------------------------------------------------------------------------
# ROTA HOME (teste)
# -----------------------------------------------------------------------------
@app.route('/')
def home():
    return jsonify({
        "status": "ok",
        "message": "Palpiteiro IA – Backend ONLINE e 100% operacional!"
    })

# -----------------------------------------------------------------------------
# ROTA – Último sorteio oficial
# -----------------------------------------------------------------------------
@app.route('/historico')
def historico():
    try:
        r = requests.get('https://api.guidi.dev.br/loteria/lotofacil/ultimo', timeout=10)
        data = r.json()
        return jsonify({"sorteios": [data]})
    except Exception as e:
        print("Erro API externa:", e)
        return jsonify({
            "sorteios": [{
                "concurso": "0000",
                "data": "N/A",
                "numeros": list(range(1, 16))
            }]
        })

# -----------------------------------------------------------------------------
# ROTA – Estatísticas (corrigida)
# -----------------------------------------------------------------------------
@app.route('/estatisticas', methods=['GET'])
def obter_estatisticas():
    try:
        if df is None:
            return jsonify({"error": "CSV não carregado no servidor"}), 500

        numeros = []

        # Extrai todas as bolas do histórico
        for i in range(1, 16):
            coluna = f"bola_{i}"
            numeros.extend(df[coluna].dropna().astype(int).tolist())

        contagem = Counter(numeros)

        mais_frequentes = sorted(contagem.items(), key=lambda x: -x[1])[:5]
        menos_frequentes = sorted(contagem.items(), key=lambda x: x[1])[:5]

        media_soma = round(
            df[[f"bola_{i}" for i in range(1, 16)]]
            .astype(float)
            .sum(axis=1)
            .mean(),
            2
        )

        return jsonify({
            "mais_frequentes": mais_frequentes,
            "menos_frequentes": menos_frequentes,
            "media_soma": media_soma
        })

    except Exception as e:
        print("Erro /estatisticas:", e)
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------------------------------------
# ROTA – Gerar palpite (com Firebase token)
# -----------------------------------------------------------------------------
@app.route('/gerar_palpites')
def gerar_palpites():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')

    if not token:
        return jsonify({"error": "Token ausente"}), 401

    try:
        decoded = fb_auth.verify_id_token(token)
        uid = decoded["uid"]
    except Exception as e:
        print("Erro token:", e)
        return jsonify({"error": "Token inválido"}), 401

    # Gera palpite aleatório
    numeros = sorted(random.sample(range(1, 26), 15))

    # Grava no Firestore
    db.collection('usuarios').document(uid).collection('apostas').add({
        'numeros': numeros,
        'timestamp': firestore.SERVER_TIMESTAMP
    })

    return jsonify({"palpites": [numeros]})

# -----------------------------------------------------------------------------
# ROTA – Minhas apostas (Firebase)
# -----------------------------------------------------------------------------
@app.route('/minhas_apostas')
def minhas_apostas():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')

    if not token:
        return jsonify({"error": "Token ausente"}), 401

    try:
        decoded = fb_auth.verify_id_token(token)
        uid = decoded["uid"]
    except:
        return jsonify({"error": "Token inválido"}), 401

    docs = (
        db.collection("usuarios")
        .document(uid)
        .collection("apostas")
        .order_by("timestamp", direction=firestore.Query.DESCENDING)
        .limit(20)
        .stream()
    )

    apostas = [doc.to_dict() for doc in docs]

    return jsonify({"apostas": apostas})

# -----------------------------------------------------------------------------
# EXECUÇÃO
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
