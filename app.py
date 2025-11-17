import os
import logging
from datetime import datetime
from functools import wraps

import pandas as pd
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

# Firebase admin imports
import firebase_admin
from firebase_admin import credentials, auth, firestore

# --- Config ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.environ.get("CSV_PATH", os.path.join(BASE_DIR, "historico_lotofacil.csv"))
APOSTA_PATH = os.environ.get("APOSTA_PATH", os.path.join(BASE_DIR, "aposta_semanal.json"))
FIREBASE_CRED_PATH = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "/etc/secrets/firebase-adminsdk.json")

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("palpiteiro-backend")

# --- Flask app ---
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# --- Firebase initialization ---
db = None
try:
    if not firebase_admin._apps:
        if os.path.exists(FIREBASE_CRED_PATH):
            cred = credentials.Certificate(FIREBASE_CRED_PATH)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin initialized using %s", FIREBASE_CRED_PATH)
        else:
            logger.warning("Firebase credential file not found at %s", FIREBASE_CRED_PATH)
    try:
        db = firestore.client()
        logger.info("Firestore client initialized.")
    except Exception as e:
        logger.warning("Could not initialize Firestore client: %s", e)
except Exception as e:
    logger.exception("Firebase initialization failed: %s", e)

# --- DataFrame load ---
try:
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH, sep=';')
        logger.info("Loaded CSV from %s", CSV_PATH)
    else:
        df = pd.DataFrame(columns=[
            'Concurso', 'Data'] + [f'bola_{i}' for i in range(1,16)] + [
            'OrdemSorteio', 'Local', 'dataProximoConcurso', 'valorEstimadoProximoConcurso'
        ])
        logger.warning("CSV not found at %s — initialized empty DataFrame", CSV_PATH)
except Exception as e:
    logger.exception("Erro ao carregar CSV de histórico: %s", e)
    df = pd.DataFrame()

# --- Utilities ---
def verify_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token ausente"}), 401
        token = auth_header.split("Bearer ")[1]
        try:
            decoded = auth.verify_id_token(token)
            request.uid = decoded.get("uid")
            return f(*args, **kwargs)
        except Exception as e:
            logger.warning("Token inválido: %s", e)
            return jsonify({"error": "Token inválido ou expirado"}), 401
    return decorated

# --- Palpites logic ---
FIXED_NUMBERS = [1, 3, 4, 15, 21, 23]

def generate_fixed_aposta():
    remaining = [n for n in range(1, 26) if n not in FIXED_NUMBERS]
    random_nums = __import__('random').sample(remaining, 9)
    return sorted(FIXED_NUMBERS + random_nums)

def generate_premium_apostas(count=7):
    palpites = []
    for _ in range(count):
        base = FIXED_NUMBERS.copy()
        remaining = [n for n in range(1, 26) if n not in base]
        additional = __import__('random').sample(remaining, 9)
        palpites.append(sorted(base + additional))
    return palpites

# --- Routes ---
@app.route("/gerar_palpites", methods=["GET"])
def gerar_palpites():
    premium = request.args.get("premium") == "true"
    fixed = request.args.get("fixed") == "true"
    try:
        if fixed:
            import json
            today = datetime.now()
            aposta = None
            if os.path.exists(APOSTA_PATH):
                with open(APOSTA_PATH, "r") as f:
                    aposta = json.load(f)
            if not aposta or today.weekday() == 6:
                aposta = generate_fixed_aposta()
                with open(APOSTA_PATH, "w") as f:
                    json.dump(aposta, f)
            return jsonify({"palpites": [aposta]})
        elif premium:
            return jsonify({"palpites": generate_premium_apostas()})
        else:
            numeros = __import__('random').sample(range(1, 26), 15)
            return jsonify({"palpites": [sorted(numeros)]})
    except Exception as e:
        logger.exception("Erro gerar_palpites: %s", e)
        return jsonify({"error": "Falha ao gerar palpites"}), 500

@app.route("/historico", methods=["GET", "OPTIONS"])
def historico():
    global df
    if request.method == "OPTIONS":
        return jsonify({}), 200
    try:
        response = requests.get("https://api.guidi.dev.br/loteria/lotofacil/ultimo", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "error":
                raise ValueError("API externa retornou erro")
            concurso = str(data.get("numero"))
            data_sorteio = data.get("dataApuracao")
            numeros = data.get("listaDezenas", [])
            ordem_sorteio = data.get("dezenasSorteadasOrdemSorteio", [])
            local_sorteio = data.get("nomeMunicipioUFSorteio")
            proximo_data = data.get("dataProximoConcurso")
            proximo_valor = data.get("valorEstimadoProximoConcurso")
            if not concurso or not data_sorteio or len(numeros) < 15:
                raise ValueError("Dados insuficientes da API externa")
            new_row = {"Concurso": concurso, "Data": data_sorteio}
            for i, n in enumerate(numeros[:15], start=1):
                new_row[f"bola_{i}"] = n
            new_row["OrdemSorteio"] = ",".join(ordem_sorteio) if ordem_sorteio else None
            new_row["Local"] = local_sorteio
            new_row["dataProximoConcurso"] = proximo_data or (datetime.strptime(data_sorteio, "%Y-%m-%d") + pd.Timedelta(days=7)).strftime("%Y-%m-%d")
            new_row["valorEstimadoProximoConcurso"] = proximo_valor or "2.000.000,00"
            try:
                if df.empty or not df['Concurso'].eq(concurso).any():
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    df.to_csv(CSV_PATH, sep=';', index=False)
            except Exception as e:
                logger.warning("Não foi possível salvar histórico localmente: %s", e)
            return jsonify({"sorteios": [new_row]})
        else:
            raise ValueError("Falha requisição API externa")
    except Exception as e:
        logger.exception("Erro na rota /historico: %s", e)
        try:
            if not df.empty:
                return jsonify({"sorteios": df.tail(10).to_dict("records")})
        except Exception:
            pass
        return jsonify({"error": "Não foi possível obter histórico"}), 500

@app.route("/estatisticas", methods=["GET"])
def estatisticas():
    global df
    try:
        numeros = []
        for i in range(1, 16):
            coluna = f"bola_{i}"
            if coluna in df:
                numeros.extend(df[coluna].dropna().astype(int).tolist())
        from collections import Counter
        contagem = Counter(numeros)
        mais_frequentes = sorted(contagem.items(), key=lambda x: -x[1])[:5]
        menos_frequentes = sorted(contagem.items(), key=lambda x: x[1])[:5]
        media_soma = round(df[[f'bola_{i}' for i in range(1,16) if f'bola_{i}' in df]].astype(float).sum(axis=1).mean(), 2) if not df.empty else 0
        return jsonify({"mais_frequentes": mais_frequentes, "menos_frequentes": menos_frequentes, "media_soma": media_soma})
    except Exception as e:
        logger.exception("Erro em /estatisticas: %s", e)
        return jsonify({"error": "Falha ao calcular estatísticas"}), 500

# Firestore helpers (use db if initialized)
def salvar_aposta_firestore(uid, numeros, concurso=None):
    if db is None:
        raise RuntimeError("Firestore não inicializado")
    doc_ref = db.collection("usuarios").document(uid).collection("apostas").document(concurso or datetime.utcnow().isoformat())
    doc_ref.set({"numeros": numeros, "concurso": concurso, "timestamp": firestore.SERVER_TIMESTAMP})
    return True

def obter_apostas_firestore(uid, limit=50):
    if db is None:
        raise RuntimeError("Firestore não inicializado")
    apostas_ref = db.collection("usuarios").document(uid).collection("apostas").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(limit)
    docs = apostas_ref.stream()
    result = []
    for doc in docs:
        d = doc.to_dict()
        d["id"] = doc.id
        result.append(d)
    return result

@app.route("/salvar_aposta", methods=["POST"])
@verify_token_required
def salvar_aposta():
    try:
        data = request.get_json()
        uid = request.uid
        numeros = data.get("numeros")
        concurso = data.get("concurso")
        if not numeros:
            return jsonify({"error": "Dados incompletos"}), 400
        salvar_aposta_firestore(uid, numeros, concurso)
        return jsonify({"status": "Aposta salva com sucesso"})
    except Exception as e:
        logger.exception("Erro em /salvar_aposta: %s", e)
        return jsonify({"error": "Não foi possível salvar aposta"}), 500

@app.route("/minhas_apostas", methods=["GET"])
@verify_token_required
def minhas_apostas():
    try:
        uid = request.uid
        apostas = obter_apostas_firestore(uid)
        return jsonify({"apostas": apostas})
    except Exception as e:
        logger.exception("Erro em /minhas_apostas: %s", e)
        return jsonify({"error": "Não foi possível obter apostas"}), 500

@app.route("/health", methods=["GET"])
def health():
    connected = db is not None
    return jsonify({"status": "ok", "firebase_connected": connected, "time": datetime.utcnow().isoformat()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))