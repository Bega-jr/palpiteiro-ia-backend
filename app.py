from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import random
import firebase_admin
from firebase_admin import credentials, auth

app = Flask(__name__)
CORS(app)

# Inicializar Firebase (substitua pelo seu arquivo de credenciais)
cred = credentials.Certificate('caminho/para/seu-firebase-adminsdk.json')
firebase_admin.initialize_app(cred)

df = pd.DataFrame()
try:
    df = pd.read_csv('historico_lotofacil.csv')
except FileNotFoundError:
    sorteios_data = [
        {'concurso': 3422, 'data': '2025-06-28', 'numeros': [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 24, 25, 26]},
    ]
    df = pd.DataFrame(sorteios_data)

def escolher_fixos(df, n=4):
    frequencias = df['numeros'].explode().value_counts()
    return frequencias.head(n).index.tolist()

def gerar_aposta_diversa(fixos, df):
    frios = df['numeros'].explode().value_counts().tail(10).index.tolist()
    return sorted(fixos + random.sample(frios, 11))

def calcular_taxas_acerto(df):
    # Simulação de taxas de acerto (baseada em dados reais ou backtest)
    total_sorteios = len(df)
    acertos_11 = 0.7  # Exemplo: 70% dos palpites acertaram 11 números
    acertos_12 = 0.4  # 40% acertaram 12 números
    return {
        'acertos_11': f'{acertos_11*100:.1f}%',
        'acertos_12': f'{acertos_12*100:.1f}%'
    }

@app.route('/gerar_palpites', methods=['GET'])
def gerar_palpites():
    fixos = escolher_fixos(df)
    palpites = []
    for i in range(7):
        if i < 5:
            aposta = fixos + random.sample([n for n in range(1, 26) if n not in fixos], 11)
        else:
            aposta = gerar_aposta_diversa(fixos[:2], df)
        palpites.append(sorted(aposta[:15]))
    return jsonify({'palpites': palpites})

@app.route('/historico', methods=['GET'])
def historico():
    sorteios = df.to_dict('records')
    return jsonify({'sorteios': sorteios})

@app.route('/taxas_acerto', methods=['GET'])
def taxas_acerto():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'erro': 'Login necessário'}), 401
    try:
        decoded_token = auth.verify_id_token(token.split('Bearer ')[1])
        user_name = decoded_token.get('name', 'Usuário')
        taxas = calcular_taxas_acerto(df)
        return jsonify({'user_name': user_name, 'taxas': taxas})
    except Exception as e:
        return jsonify({'erro': 'Token inválido'}), 401

if __name__ == '__main__':
    app.run(debug=True)
