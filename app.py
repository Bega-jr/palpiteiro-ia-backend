import requests
import pandas as pd
from flask import Flask, jsonify, request
import os
from flask_cors import CORS
import json
import random
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Caminhos e dados
csv_path = 'historico_lotofacil.csv'
aposta_path = 'aposta_semanal.json'

# Carregar ou inicializar DataFrame
df = pd.read_csv(csv_path, sep=';') if os.path.exists(csv_path) else pd.DataFrame(columns=[
    'Concurso', 'Data', 'bola_1', 'bola_2', 'bola_3', 'bola_4', 'bola_5', 'bola_6', 'bola_7', 'bola_8', 'bola_9', 'bola_10',
    'bola_11', 'bola_12', 'bola_13', 'bola_14', 'bola_15', 'OrdemSorteio', 'Local', 'ValorPremio15', 'Ganhadores15',
    'ValorPremio14', 'Ganhadores14', 'ValorPremio13', 'Ganhadores13', 'ValorPremio12', 'Ganhadores12', 'ValorPremio11',
    'Ganhadores11'
])

# Números consistentes baseados no histórico
FIXED_NUMBERS = [1, 3, 4, 15, 21, 23]

# Carregar aposta semanal
def load_weekly_aposta():
    if os.path.exists(aposta_path):
        with open(aposta_path, 'r') as f:
            return json.load(f)
    return None

# Salvar aposta semanal
def save_weekly_aposta(aposta):
    with open(aposta_path, 'w') as f:
        json.dump(aposta, f)

# Gerar aposta fixa semanal
def generate_fixed_aposta():
    remaining = [n for n in range(1, 26) if n not in FIXED_NUMBERS]
    random_nums = random.sample(remaining, 9)
    return sorted(FIXED_NUMBERS + random_nums)

# Gerar 7 apostas premium
def generate_premium_apostas():
    palpites = []
    for _ in range(7):
        base = FIXED_NUMBERS.copy()
        remaining = [n for n in range(1, 26) if n not in base]
        additional = random.sample(remaining, 9)
        palpites.append(sorted(base + additional))
    return palpites

@app.route('/gerar_palpites', methods=['GET'])
def gerar_palpites():
    try:
        premium = request.args.get('premium') == 'true'
        fixed = request.args.get('fixed') == 'true'

        if fixed:
            today = datetime.now()
            aposta = load_weekly_aposta()
            if not aposta or today.weekday() == 6:  # 6 = Domingo
                aposta = generate_fixed_aposta()
                save_weekly_aposta(aposta)
            return jsonify({'palpites': [aposta]})
        elif premium:
            palpites = generate_premium_apostas()
            return jsonify({'palpites': palpites})
        else:
            numeros = random.sample(range(1, 26), 15)
            return jsonify({'palpites': [numeros]})
    except Exception as e:
        print(f"Erro ao gerar palpites: {e}")
        return jsonify({'error': 'Falha ao gerar palpites'}), 500

@app.route('/historico', methods=['GET', 'OPTIONS'])
def historico():
    global df
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        response = requests.get('https://api.guidi.dev.br/loteria/lotofacil/ultimo', timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'error':
                raise ValueError("API retornou erro")
            concurso = str(data.get('numero'))
            data_sorteio = data.get('dataApuracao')
            numeros = data.get('listaDezenas', [])
            ordem_sorteio = data.get('dezenasSorteadasOrdemSorteio', [])
            local_sorteio = data.get('nomeMunicipioUFSorteio')
            if not concurso or not data_sorteio or not numeros or len(numeros) < 15:
                raise ValueError("Dados insuficientes da API")
            
            new_row = {
                'Concurso': concurso,
                'Data': data_sorteio,
                'bola_1': numeros[0], 'bola_2': numeros[1], 'bola_3': numeros[2], 'bola_4': numeros[3],
                'bola_5': numeros[4], 'bola_6': numeros[5], 'bola_7': numeros[6], 'bola_8': numeros[7],
                'bola_9': numeros[8], 'bola_10': numeros[9], 'bola_11': numeros[10], 'bola_12': numeros[11],
                'bola_13': numeros[12], 'bola_14': numeros[13], 'bola_15': numeros[14],
                'OrdemSorteio': ','.join(ordem_sorteio) if ordem_sorteio else None,
                'Local': local_sorteio
            }
            
            rateio_premio = data.get('listaRateioPremio', [])
            for faixa in rateio_premio:
                acertos = 16 - faixa['faixa']
                if 11 <= acertos <= 15:
                    valor_premio = float(faixa['valorPremio']) if faixa['valorPremio'] else 0
                    ganhadores = int(faixa['numeroDeGanhadores']) if faixa['numeroDeGanhadores'] else 0
                    new_row[f'ValorPremio{acertos}'] = valor_premio
                    new_row[f'Ganhadores{acertos}'] = ganhadores

            for acertos in range(11, 16):
                new_row[f'ValorPremio{acertos}'] = new_row.get(f'ValorPremio{acertos}', 0)
                new_row[f'Ganhadores{acertos}'] = new_row.get(f'Ganhadores{acertos}', 0)

            if not df['Concurso'].eq(concurso).any():
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                df.to_csv(csv_path, sep=';', index=False)
            
            # Simular próximo sorteio (a ser ajustado com API real)
            proximo_concurso = int(concurso) + 1
            proximo_data = (datetime.strptime(data_sorteio, '%Y-%m-%d') + pd.Timedelta(days=7)).strftime('%Y-%m-%d')
            proximo_row = {
                'Concurso': str(proximo_concurso),
                'dataProximoConcurso': proximo_data,
                'local': local_sorteio,  # Mesma cidade como exemplo
                'valorEstimadoProximoConcurso': '2.000.000,00'  # Estimativa fictícia
            }
            return jsonify({'sorteios': [new_row, proximo_row]})
        else:
            raise ValueError("Falha na requisição à API")
    except Exception as e:
        print(f"Erro ao processar API: {e}")
        if not df.empty:
            return jsonify({'sorteios': df.to_dict('records')})
        return jsonify({'sorteios': [{
            'Concurso': '3436', 'Data': '2025-07-07', 'bola_1': '01', 'bola_2': '02', 'bola_3': '03', 'bola_4': '04',
            'bola_5': '05', 'bola_6': '06', 'bola_7': '07', 'bola_8': '08', 'bola_9': '09', 'bola_10': '10',
            'bola_11': '11', 'bola_12': '12', 'bola_13': '13', 'bola_14': '14', 'bola_15': '15',
            'OrdemSorteio': '01,02,03,04,05,06,07,08,09,10,11,12,13,14,15', 'Local': 'SÃO PAULO, SP',
            'ValorPremio15': 1806333.97, 'Ganhadores15': 1, 'ValorPremio14': 2181.72, 'Ganhadores14': 248,
            'ValorPremio13': 30.0, 'Ganhadores13': 9800, 'ValorPremio12': 12.0, 'Ganhadores12': 111936,
            'ValorPremio11': 6.0, 'Ganhadores11': 627357
        }]}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
