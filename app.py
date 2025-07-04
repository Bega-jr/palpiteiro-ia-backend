import requests
import pandas as pd
from flask import Flask, jsonify, request
import os

app = Flask(__name__)

# Carregar ou criar o CSV
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
        # Buscar dados da API da Caixa
        response = requests.get('https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil/latest')
        if response.status_code != 200:
            raise ValueError(f"Erro na API: {response.status_code}")
        data = response.json()

        # Extrair informações
        concurso = data['numero']
        data_sorteio = data['dataApuracao']
        numeros = data['dezenas']

        # Verificar se o concurso já existe
        if df['Concurso'].eq(concurso).any():
            return jsonify({'sorteios': df.to_dict('records')})

        # Adicionar novo sorteio ao DataFrame
        new_row = {'Concurso': concurso, 'Data': data_sorteio}
        for i, num in enumerate(numeros, 1):
            new_row[f'bola_{i}'] = num
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        # Salvar no CSV
        df.to_csv(csv_path, sep=';', index=False)

        # Retornar os sorteios atualizados
        return jsonify({'sorteios': df.to_dict('records')})
    except Exception as e:
        print(f"Erro na rota /historico: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
