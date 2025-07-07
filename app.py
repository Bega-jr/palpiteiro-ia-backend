import requests
import pandas as pd
from flask import Flask, jsonify, request
import os
from flask_cors import CORS
import json
import random

app = Flask(__name__)
CORS(app)

csv_path = 'historico_lotofacil.csv'
if os.path.exists(csv_path):
    df = pd.read_csv(csv_path, sep=';')
else:
    df = pd.DataFrame(columns=['Concurso', 'Data', 'bola_1', 'bola_2', 'bola_3', 'bola_4', 'bola_5', 'bola_6', 'bola_7', 'bola_8', 'bola_9', 'bola_10', 'bola_11', 'bola_12', 'bola_13', 'bola_14', 'bola_15'])

@app.route('/historico', methods=['GET', 'OPTIONS'])
def historico():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        response = requests.get('https://api.guidi.dev.br/loteria/lotofacil/ultimo', timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"Resposta da API: {json.dumps(data, indent=2)}")
            if data.get('status') == 'error':
                raise ValueError(f"API retornou erro: {data.get('message')}")
            concurso = str(data.get('concurso') or data.get('numero'))
            data_sorteio = data.get('data') or data.get('dataApuracao')
            numeros = data.get('dezenas', [])
            if not concurso or not data_sorteio or not numeros or len(numeros) < 15:
                raise ValueError(f"Estrutura da API inválida ou dados insuficientes. Resposta: {json.dumps(data, indent=2)}")
            if not df['Concurso'].eq(concurso).any():
                new_row = {'Concurso': concurso, 'Data': data_sorteio}
                for i, num in enumerate(numeros[:15], 1):
                    new_row[f'bola_{i}'] = num
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                df.to_csv(csv_path, sep=';', index=False)
                print(f"Novo concurso adicionado: {concurso}")
        else:
            print(f"API falhou com status: {response.status_code}, texto: {response.text}")
    except Exception as e:
        print(f"Erro na rota /historico: {e}")
    if df.empty:
        df = pd.DataFrame([{'Concurso': '3430', 'Data': '2025-06-30', 'bola_1': '01', 'bola_2': '02', 'bola_3': '03', 'bola_4': '04', 'bola_5': '05', 'bola_6': '06', 'bola_7': '07', 'bola_8': '08', 'bola_9': '09', 'bola_10': '10', 'bola_11': '11', 'bola_12': '12', 'bola_13': '13', 'bola_14': '14', 'bola_15': '15'}])
    return jsonify({'sorteios': df.to_dict('records')})

@app.route('/gerar_palpites', methods=['GET'])
def gerar_palpites():
    try:
        numeros = random.sample(range(1, 26), 15)  # Gera 15 números únicos de 1 a 25
        return jsonify({'palpites': [numeros]})
    except Exception as e:
        print(f"Erro ao gerar palpites: {e}")
        return jsonify({'error': 'Falha ao gerar palpites'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
