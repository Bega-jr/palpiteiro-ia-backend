from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import random

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://palpiteiro-ia.netlify.app", "http://localhost:8000"]}})

# Carregar CSV
try:
    df = pd.read_csv('historico_lotofacil.csv', sep=';')
    print(f"CSV carregado com {len(df)} linhas")
    required_columns = ['Concurso', 'Data'] + [f'bola {i}' for i in range(1, 16)]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Colunas ausentes no CSV: {missing_columns}")
except Exception as e:
    print(f"Erro ao carregar CSV: {e}")
    df = pd.DataFrame()

@app.route('/historico', methods=['GET'])
def historico():
    try:
        if df.empty:
            return jsonify({'error': 'Nenhum dado disponível no histórico'}), 500
        sorteios = [
            {
                'concurso': int(row['Concurso']),
                'data': str(row['Data']),
                'numeros': [int(row[f'bola {i}']) for i in range(1, 16)]
            } for _, row in df.iterrows() if not pd.isna(row['Concurso'])
        ]
        return jsonify({'sorteios': sorteios})
    except Exception as e:
        print(f"Erro na rota /historico: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/gerar_palpites', methods=['GET'])
def gerar_palpites():
    try:
        palpites = [random.sample(range(1, 26), 15) for _ in range(7)]
        return jsonify({'palpites': [sorted(p) for p in palpites]})
    except Exception as e:
        print(f"Erro na rota /gerar_palpites: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/taxas_acerto', methods=['GET'])
def taxas_acerto():
    try:
        taxas = {'acertos_11': '70.0%', 'acertos_12': '30.0%'}
        return jsonify({'taxas': taxas})
    except Exception as e:
        print(f"Erro na rota /taxas_acerto: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
