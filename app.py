import os
import json
import random
import requests
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
from auth_middleware import verificar_token
import firestore_utils as fs

app = Flask(__name__)
CORS(app)

# ---------- CACHE EM MEMÓRIA ----------
_cache = {}
_cache_time = {}

def cached(key, ttl=3600):
    now = datetime.now()
    if key in _cache and now - _cache_time.get(key, now) < timedelta(seconds=ttl):
        return _cache[key]
    return None

def set_cached(key, value, ttl=3600):
    _cache[key] = value
    _cache_time[key] = datetime.now()

# ---------- IA ----------
FIXED_NUMBERS = [1, 3, 4, 15, 21, 23]

def gerar_palpite_com_peso():
    stats = cached('estatisticas') or update_estatisticas_cache()
    contagem = dict(stats['mais_frequentes'] + stats['menos_frequentes'])
    pesos = [contagem.get(i, 1) for i in range(1, 26)]
    return sorted(random.choices(range(1, 26), weights=pesos, k=15))

def update_estatisticas_cache():
    docs = fs.db.collection('lotofacil_historico').stream()
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
    soma_media = 195  # fallback
    stats = {'mais_frequentes': mais, 'menos_frequentes': menos, 'media_soma': soma_media}
    set_cached('estatisticas', stats, 3600)
    return stats

# ---------- ROTAS ----------
@app.route('/gerar_palpites', methods=['GET'])
@verificar_token
def gerar_palpites():
    try:
        tipo = request.args.get('tipo', 'aleatorio')
        uid = request.uid

        if tipo == 'fixo':
            aposta = {'numeros': sorted(FIXED_NUMBERS + random.sample([n for n in range(1,26) if n not in FIXED_NUMBERS], 9))}
            fs.salvar_aposta(uid, aposta['numeros'], 'fixa_semanal')
            return jsonify({'palpites': [aposta['numeros']]})

        elif tipo == 'estatistico':
            palpite = gerar_palpite_com_peso()
            fs.salvar_aposta(uid, palpite, f'estatistico_{int(datetime.now().timestamp())}')
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

    cached_data = cached('lotofacil_ultimo')
    if cached_data:
        return jsonify({'sorteios': [cached_data]})

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
            'local': data.get('nomeMunicipioUFSorteio', 'SP'),
            'proximo_concurso': data.get('dataProximoConcurso'),
            'valor_estimado': data.get('valorEstimadoProximoConcurso', '2.000.000,00')
        }

        fs.db.collection('lotofacil_historico').document(concurso).set(doc_data, merge=True)
        set_cached('lotofacil_ultimo', doc_data, 3600)
        update_estatisticas_cache()
        return jsonify({'sorteios': [doc_data]})

    except Exception as e:
        print(e)
        return jsonify({'sorteios': []}), 500

@app.route('/minhas_apostas', methods=['GET'])
@verificar_token
def minhas_apostas():
    uid = request.uid
    apostas = fs.obter_apostas(uid)
    return jsonify({'apostas': apostas})

@app.route('/estatisticas', methods=['GET'])
def estatisticas():
    stats = cached('estatisticas') or update_estatisticas_cache()
    return jsonify(stats)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
