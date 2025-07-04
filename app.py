import requests
import pandas as pd
from flask import Flask, jsonify, request
import os
from flask_cors import CORS

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
            # Tentar diferentes chaves pra mapear os dados
            concurso = data.get('concurso') or data.get('concurso_id') or data.get('numero')
            data_sorteio = data.get('data') or data.get('data_sorteio') or data.get('dataApuracao')
            numeros = data.get('dezenas', [])
            if not concurso or not data_sorteio or not numeros:
                raise ValueError(f"Estrutura da API inválida ou dados ausentes. Resposta: {data}")
            if not df['Concurso'].eq(concurso).any():
                new_row = {'Concurso': concurso, 'Data': data_sorteio}
                for i, num in enumerate(numeros[:15], 1):
                    new_row[f'bola_{i}'] = num
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                df.to_csv(csv_path, sep=';', index=False)
                print(f"Novo concurso adicionado: {concurso}")
        else:
            raise ValueError(f"Erro na API: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Erro na rota /historico: {e}")
        # Fallback pra dados existentes no CSV
        if not df.empty:
            return jsonify({'sorteios': df.to_dict('records')})
        return jsonify({'error': str(e)}), 500

    return jsonify({'sorteios': df.to_dict('records')})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
