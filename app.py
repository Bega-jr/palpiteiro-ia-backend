import os
import json
import random
import requests
import pandas as pd
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
import redis
from auth_middleware import verificar_token
import firestore_utils as fs

app = Flask(__name__)
CORS(app)

# ---------- CONFIG ----------
CSV_PATH = 'historico_lotofacil.csv'
APOSTA_PATH = 'aposta_semanal.json'
REDIS = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'), decode_responses=True)

# Carregar CSV (fallback)
df = pd.read_csv(CSV_PATH, sep=';') if os.path.exists(CSV_PATH) else pd.DataFrame()

# Números fixos
FIXED_NUMBERS = [1, 3, 4, 15, 21, 23]

# ---------- HELPERS ----------
def load_weekly_aposta():
    if os.path.exists(APOSTA_PATH):
        with open(APOSTA_PATH) as f:
            return json.load(f)
    return None

def save_weekly_aposta(aposta):
    with open(APOSTA_PATH, 'w') as f:
        json.dump(aposta, f)

def generate_fixed_aposta():
    remaining = [n for n in range(1, 26) if n not in FIXED_NUMBERS]
    return sorted(FIXED_NUMBERS + random.sample(remaining, 9))

def generate_premium_apostas():
    return [sorted(FIXED_NUMBERS + random.sample([n for n in range(1,26) if n not in FIXED_NUMBERS], 9)) for _ in range(7)]

# ---------- ROTAS ----------
@app.route('/gerar_palpites', methods=['GET'])
@verificar_token
def gerar_palpites():
    try:
        premium = request.args.get('premium') == 'true'
        fixed = request.args.get('fixed') == 'true'
        uid = request.uid

        if fixed:
            today = datetime.now()
            aposta = load_weekly_aposta()
            if not aposta or today.weekday() == 6:  # Domingo
                aposta = generate_fixed_aposta()
                save_weekly_aposta(aposta)
            fs.salvar_aposta(uid, aposta, "fixa_semanal")
            return jsonify({'palpites': [aposta]})

        elif premium:
            palpites = generate_premium_apostas()
            return jsonify({'palpites': palpites})

        else:
            nums = sorted(random.sample(range(1, 26), 15))
            fs.salvar_aposta(uid, nums, f"aleatoria_{int(datetime.now().timestamp())}")
            return jsonify({'palpites': [nums]})

    except Exception as e:
        return jsonify({'error': 'Falha ao gerar palpites'}), 500

@app.route('/historico', methods=['GET', 'OPTIONS'])
def historico():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    cached = REDIS.get('lotofacil_ultimo')
    if cached:
        return jsonify({'sorteios': [json.loads(cached)]})

    try:
        resp = requests.get('https://api.guidi.dev.br/loteria/lotofacil/ultimo', timeout=10)
        if resp.status_code != 200 or resp.json().get('status') == 'error':
            raise ValueError("API indisponível")

        data = resp.json()
        concurso = str(data['numero'])
        numeros = data['listaDezenas'][:15]
        new_row = {
            'Concurso': concurso,
            'Data': data['dataApuracao'],
            **{f'bola_{i+1}': int(n) for i, n in enumerate(numeros)},
            'Local': data.get('nomeMunicipioUFSorteio', 'Não informado'),
            'dataProximoConcurso': data.get('dataProximoConcurso'),
            'valorEstimadoProximoConcurso': data.get('valorEstimadoProximoConcurso', '2.000.000,00')
        }

        # Cache 1h
        REDIS.setex('lotofacil_ultimo', 3600, json.dumps(new_row))
        return jsonify({'sorteios': [new_row]})

    except Exception as e:
        print(f"Erro API: {e}")
        if not df.empty:
            last = df.tail(1).to_dict('records')[0]
            return jsonify({'sorteios': [last]})
        return jsonify({'sorteios': [{
            'Concurso': '3436', 'Data': '2025-07-07',
            'bola_1': 1, 'bola_2': 2, 'bola_3': 3, 'bola_4': 4, 'bola_5': 5,
            'bola_6': 6, 'bola_7': 7, 'bola_8': 8, 'bola_9': 9, 'bola_10': 10,
            'bola_11': 11, 'bola_12': 12, 'bola_13': 13, 'bola_14': 14, 'bola_15': 15,
            'Local': 'SÃO PAULO, SP',
            'dataProximoConcurso': '2025-07-14',
            'valorEstimadoProximoConcurso': '2.000.000,00'
        }]})

@app.route('/minhas_apostas', methods=['GET'])
@verificar_token
def minhas_apostas():
    uid = request.uid
    apostas = fs.obter_apostas(uid)
    return jsonify({'apostas': apostas})

# ---------- ESTATÍSTICAS ----------
@app.route('/estatisticas', methods=['GET'])
def estatisticas():
    global df
    try:
        if df.empty:
            return jsonify({'mais_frequentes': [], 'menos_frequentes': [], 'media_soma': 0})

        numeros = []
        for i in range(1, 16):
            col = f'bola_{i}'
            if col in df.columns:
                numeros.extend(df[col].dropna().astype(int).tolist())

        from collections import Counter
        contagem = Counter(numeros)
        mais_frequentes = sorted(contagem.items(), key=lambda x: -x[1])[:5]
        menos_frequentes = sorted(contagem.items(), key=lambda x: x[1])[:5]
        soma_media = round(df[[f'bola_{i}' for i in range(1, 16) if f'bola_{i}' in df.columns]].sum(axis=1).mean(), 2)

        return jsonify({
            'mais_frequentes': mais_frequentes,
            'menos_frequentes': menos_frequentes,
            'media_soma': soma_media
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
