import os
import json
import random
import requests
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
import redis
from auth_middleware import verificar_token
import firestore_utils as fs

app = Flask(__name__)
CORS(app)

# ---------- CONFIG ----------
REDIS = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'), decode_responses=True)
COLLECTION_HISTORICO = 'lotofacil_historico'
COLLECTION_ESTATISTICAS = 'lotofacil_estatisticas'

# Números fixos (base da IA)
FIXED_NUMBERS = [1, 3, 4, 15, 21, 23]

# ---------- HELPERS ----------
def get_historico_from_firestore():
    docs = fs.db.collection(COLLECTION_HISTORICO).order_by('data', direction='DESCENDING').limit(100).stream()
    return [doc.to_dict() for doc in docs]

def get_estatisticas_cached():
    cached = REDIS.get('estatisticas')
    if cached:
        return json.loads(cached)
    return None

def update_estatisticas_cache():
    docs = fs.db.collection(COLLECTION_HISTORICO).stream()
    numeros = []
    for doc in docs:
        data = doc.to_dict()
        for i in range(1, 16):
            key = f'bola_{i}'
            if key in data:
                numeros.append(int(data[key]))
    
    from collections import Counter
    contagem = Counter(numeros)
    mais = sorted(contagem.items(), key=lambda x: -x[1])[:5]
    menos = sorted(contagem.items(), key=lambda x: x[1])[:5]
    soma_media = round(sum(sum(int(data.get(f'bola_{i}', 0)) for i in range(1,16)) for data in get_historico_from_firestore()) / len(numeros), 2)
    
    stats = {
        'mais_frequentes': mais,
        'menos_frequentes': menos,
        'media_soma': soma_media,
        'atualizado_em': datetime.now().isoformat()
    }
    REDIS.setex('estatisticas', 3600, json.dumps(stats))
    return stats

# ---------- IA: PALPITES COM PESO ----------
def gerar_palpite_com_peso():
    stats = get_estatisticas_cached() or update_estatisticas_cache()
    contagem = dict(stats['mais_frequentes'] + stats['menos_frequentes'])
    pesos = [contagem.get(i, 1) for i in range(1, 26)]  # mínimo 1
    return sorted(random.choices(range(1, 26), weights=pesos, k=15))

def gerar_palpite_markov():
    historico = get_historico_from_firestore()
    if len(historico) < 2:
        return sorted(random.sample(range(1, 26), 15))
    
    ultimo = {int(historico[0][f'bola_{i}']) for i in range(1,16) if f'bola_{i}' in historico[0]}
    transicoes = {}
    
    for i in range(1, len(historico)):
        atual = {int(historico[i][f'bola_{j}']) for j in range(1,16) if f'bola_{j}' in historico[i]}
        for num in atual:
            if num not in transicoes:
                transicoes[num] = []
            transicoes[num].extend(ultimo - atual)
        ultimo = atual
    
    candidatos = []
    for _ in range(15):
        if random.random() < 0.6 and ultimo:
            proximo = random.choice(list(ultimo))
        else:
            proximo = random.choices(range(1,26), weights=[transicoes.get(n, [1]*25)[0] for n in range(1,26)], k=1)[0]
        candidatos.append(proximo)
        ultimo.add(proximo)
    
    return sorted(set(candidatos) | set(random.sample(range(1,26), 15 - len(candidatos))))

# ---------- ROTAS ----------
@app.route('/gerar_palpites', methods=['GET'])
@verificar_token
def gerar_palpites():
    try:
        tipo = request.args.get('tipo', 'aleatorio')  # aleatorio, estatistico, markov, premium, fixo
        uid = request.uid

        if tipo == 'fixo':
            aposta = fs.db.collection('apostas_fixas').document('semanal').get().to_dict()
            if not aposta or datetime.now().weekday() == 6:
                aposta = {'numeros': sorted(FIXED_NUMBERS + random.sample([n for n in range(1,26) if n not in FIXED_NUMBERS], 9))}
                fs.db.collection('apostas_fixas').document('semanal').set(aposta)
            fs.salvar_aposta(uid, aposta['numeros'], 'fixa_semanal')
            return jsonify({'palpites': [aposta['numeros']]})

        elif tipo == 'premium':
            palpites = [sorted(FIXED_NUMBERS + random.sample([n for n in range(1,26) if n not in FIXED_NUMBERS], 9)) for _ in range(7)]
            return jsonify({'palpites': palpites})

        elif tipo == 'estatistico':
            palpite = gerar_palpite_com_peso()
            fs.salvar_aposta(uid, palpite, f'estatistico_{int(datetime.now().timestamp())}')
            return jsonify({'palpites': [palpite]})

        elif tipo == 'markov':
            palpite = gerar_palpite_markov()
            fs.salvar_aposta(uid, palpite, f'markov_{int(datetime.now().timestamp())}')
            return jsonify({'palpites': [palpite]})

        else:
            nums = sorted(random.sample(range(1, 26), 15))
            fs.salvar_aposta(uid, nums, f'aleatorio_{int(datetime.now().timestamp())}')
            return jsonify({'palpites': [nums]})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/historico', methods=['GET', 'OPTIONS'])
def historico():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    cached = REDIS.get('lotofacil_ultimo')
    if cached:
        return jsonify({'sorteios': [json.loads(cached)]})

    try:
        resp = requests.get('https://api.guidi.dev.br/loteria/lotofacil/ultimo', timeout=10)
        data = resp.json()
        if resp.status_code != 200 or data.get('status') == 'error':
            raise ValueError("API error")

        concurso = str(data['numero'])
        numeros = data['listaDezenas'][:15]
        doc_data = {
            'concurso': concurso,
            'data': data['dataApuracao'],
            **{f'bola_{i+1}': int(n) for i, n in enumerate(numeros)},
            'local': data.get('nomeMunicipioUFSorteio', 'Não informado'),
            'proximo_concurso': data.get('dataProximoConcurso'),
            'valor_estimado': data.get('valorEstimadoProximoConcurso', '2.000.000,00'),
            'atualizado_em': firestore.SERVER_TIMESTAMP
        }

        # Salva no Firestore
        fs.db.collection(COLLECTION_HISTORICO).document(concurso).set(doc_data, merge=True)
        REDIS.setex('lotofacil_ultimo', 3600, json.dumps(doc_data))
        update_estatisticas_cache()  # Atualiza stats
        return jsonify({'sorteios': [doc_data]})

    except Exception as e:
        print(e)
        # Fallback: último do Firestore
        doc = fs.db.collection(COLLECTION_HISTORICO).order_by('data', direction='DESCENDING').limit(1).stream()
        fallback = next(doc, None)
        if fallback:
            data = fallback.to_dict()
            return jsonify({'sorteios': [data]})
        return jsonify({'sorteios': []}), 500

@app.route('/minhas_apostas', methods=['GET'])
@verificar_token
def minhas_apostas():
    uid = request.uid
    apostas = fs.obter_apostas(uid)
    return jsonify({'apostas': apostas})

@app.route('/estatisticas', methods=['GET'])
def estatisticas():
    stats = get_estatisticas_cached()
    if not stats:
        stats = update_estatisticas_cache()
    return jsonify(stats)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
