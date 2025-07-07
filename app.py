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
# Carrega o CSV globalmente, fora da função
df = pd.read_csv(csv_path, sep=';') if os.path.exists(csv_path) else pd.DataFrame(columns=['Concurso', 'Data', 'bola_1', 'bola_2', 'bola_3', 'bola_4', 'bola_5', 'bola_6', 'bola_7', 'bola_8', 'bola_9', 'bola_10', 'bola_11', 'bola_12', 'bola_13', 'bola_14', 'bola_15', 'OrdemSorteio', 'Local', 'ValorPremio15', 'Ganhadores15', 'ValorPremio14', 'Ganhadores14', 'ValorPremio13', 'Ganhadores13', 'ValorPremio12', 'Ganhadores12', 'ValorPremio11', 'Ganhadores11'])

@app.route('/historico', methods=['GET', 'OPTIONS'])
def historico():
    global df  # Garante que df seja global
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    try:
        # Tentativa de buscar e processar dados da API
        response = requests.get('https://api.guidi.dev.br/loteria/lotofacil/ultimo', timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"Resposta da API: {json.dumps(data, indent=2)}")
            if data.get('status') == 'error':
                print(f"API retornou erro: {data.get('message')}")
                raise ValueError("API retornou erro")
            concurso = str(data.get('numero'))
            data_sorteio = data.get('dataApuracao')
            numeros = data.get('listaDezenas', [])
            ordem_sorteio = data.get('dezenasSorteadasOrdemSorteio', [])
            local_sorteio = data.get('nomeMunicipioUFSorteio')
            if not concurso or not data_sorteio or not numeros or len(numeros) < 15:
                print(f"Estrutura da API inválida ou dados insuficientes: {json.dumps(data, indent=2)}")
                raise ValueError("Dados insuficientes da API")
            
            # Inicializa new_row com os campos básicos
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
            
            # Adiciona as faixas de premiação (15 a 11 acertos)
            for faixa in data.get('listaRateioPremio', []):
                acertos = faixa['faixa']
                if 11 <= acertos <= 15:
                    new_row[f'ValorPremio{acertos}'] = faixa['valorPremio']
                    new_row[f'Ganhadores{acertos}'] = faixa['numeroDeGanhadores']

            # Garante valores padrão se a faixa não existir
            for acertos in range(11, 16):
                new_row[f'ValorPremio{acertos}'] = new_row.get(f'ValorPremio{acertos}', 0)
                new_row[f'Ganhadores{acertos}'] = new_row.get(f'Ganhadores{acertos}', 0)

            if not df['Concurso'].eq(concurso).any():
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                df.to_csv(csv_path, sep=';', index=False)
                print(f"Novo concurso adicionado: {concurso}")
            return jsonify({'sorteios': [new_row]})  # Retorna apenas o último concurso da API
        else:
            print(f"API falhou com status: {response.status_code}, texto: {response.text}")
            raise ValueError("Falha na requisição à API")
    except Exception as e:
        print(f"Erro ao processar API: {e}")
        # Fallback para o CSV apenas se a API falhar
        if not df.empty:
            print("Usando fallback do CSV")
            return jsonify({'sorteios': df.to_dict('records')})
        print("CSV vazio e API falhou, retornando dados padrão")
        return jsonify({'sorteios': [{'Concurso': '3430', 'Data': '2025-06-30', 'bola_1': '01', 'bola_2': '02', 'bola_3': '03', 'bola_4': '04', 'bola_5': '05', 'bola_6': '06', 'bola_7': '07', 'bola_8': '08', 'bola_9': '09', 'bola_10': '10', 'bola_11': '11', 'bola_12': '12', 'bola_13': '13', 'bola_14': '14', 'bola_15': '15', 'OrdemSorteio': None, 'Local': None, 'ValorPremio15': 0, 'Ganhadores15': 0, 'ValorPremio14': 0, 'Ganhadores14': 0, 'ValorPremio13': 0, 'Ganhadores13': 0, 'ValorPremio12': 0, 'Ganhadores12': 0, 'ValorPremio11': 0, 'Ganhadores11': 0}]}), 500

@app.route('/gerar_palpites', methods=['GET'])
def gerar_palpites():
    try:
        numeros = random.sample(range(1, 26), 15)
        return jsonify({'palpites': [numeros]})
    except Exception as e:
        print(f"Erro ao gerar palpites: {e}")
        return jsonify({'error': 'Falha ao gerar palpites'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
