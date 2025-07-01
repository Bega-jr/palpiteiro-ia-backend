import sys
import traceback
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import random
import firebase_admin
from firebase_admin import credentials, auth
import os

app = Flask(__name__)
CORS(app)

# Depuração: Logar início do script
print("Iniciando app.py...", file=sys.stderr)

# Depuração: Verificar variável de ambiente
print(f"GOOGLE_APPLICATION_CREDENTIALS: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}", file=sys.stderr)

# Verificar se o arquivo firebase-adminsdk.json existe
try:
    with open(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'), 'r') as f:
        print("Arquivo firebase-adminsdk.json encontrado.", file=sys.stderr)
except Exception as e:
    print(f"Erro ao acessar firebase-adminsdk.json: {str(e)}", file=sys.stderr)
    raise

# Inicializar Firebase
try:
    cred = credentials.Certificate(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
    firebase_admin.initialize_app(cred)
    print("Firebase inicializado com sucesso.", file=sys.stderr)
except Exception as e:
    print(f"Erro ao inicializar Firebase: {str(e)}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    raise

# Carregar CSV com separador ';'
df = pd.DataFrame()
try:
    print("Tentando carregar historico_lotofacil.csv...", file=sys.stderr)
    df = pd.read_csv('historico_lotofacil.csv', sep=';')
    print(f"CSV carregado com sucesso. Colunas: {df.columns.tolist()}", file=sys.stderr)
except FileNotFoundError:
    print("Arquivo historico_lotofacil.csv não encontrado. Usando dados simulados.", file=sys.stderr)
    sorteios_data = [
        {'Concurso': 3422, 'Data': '2025-06-28', 'bola 1': 1, 'bola 2': 3, 'bola 3': 5, 'bola 4': 7, 'bola 5': 9,
         'bola 6': 11, 'bola 7': 13, 'bola 8': 15, 'bola 9': 17, 'bola 10': 19, 'bola 11': 21, 'bola 12': 23,
         'bola 13': 24, 'bola 14': 25, 'bola 15': 26}
    ]
    df = pd.DataFrame(sorteios_data)
except Exception as e:
    print(f"Erro ao carregar CSV: {str(e)}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    raise

# Combinar colunas bola 1 a bola 15 em uma coluna 'numeros'
try:
    print("Processando colunas 'bola 1' a 'bola 15'...", file=sys.stderr)
    bola_cols = [f'bola {i}' for i in range(1, 16)]
    if all(col in df.columns for col in bola_cols):
        df['numeros'] = df[bola_cols].apply(lambda row: [int(x) for x in row], axis=1)
        df = df[['Concurso', 'Data', 'numeros']]  # Manter apenas colunas necessárias
        df.columns = ['concurso', 'data', 'numeros']  # Padronizar nomes
    else:
        raise ValueError("Colunas 'bola 1' a 'bola 15' não encontradas no CSV")
    print("Coluna 'numeros' criada com sucesso.", file=sys.stderr)
except Exception as e:
    print(f"Erro ao processar colunas 'bola': {str(e)}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    raise

def escolher_fixos(df, n=4):
    try:
        frequencias = df['numeros'].explode().value_counts()
        return frequencias.head(n).index.tolist()
    except Exception as e:
        print(f"Erro em escolher_fixos: {str(e)}", file=sys.stderr)
        raise

def gerar_aposta_diversa(fixos, df):
    try:
        frios = df['numeros'].explode().value_counts().tail(10).index.tolist()
        return sorted(fixos + random.sample(frios, 11))
    except Exception as e:
        print(f"Erro em gerar_aposta_diversa: {str(e)}", file=sys.stderr)
        raise

def calcular_taxas_acerto(df):
    try:
        total_sorteios = len(df)
        acertos_11 = 0.7  # Simulação: 70% acertam 11 números
        acertos_12 = 0.4  # Simulação: 40% acertam 12 números
        return {
            'acertos_11': f'{acertos_11*100:.1f}%',
            'acertos_12': f'{acertos_12*100:.1f}%'
        }
    except Exception as e:
        print(f"Erro em calcular_taxas_acerto: {str(e)}", file=sys.stderr)
        raise

@app.route('/gerar_palpites', methods=['GET'])
def gerar_palpites():
    try:
        fixos = escolher_fixos(df)
        palpites = []
        for i in range(7):
            if i < 5:
                aposta = fixos + random.sample([n for n in range(1, 26) if n not in fixos], 11)
            else:
                aposta = gerar_aposta_diversa(fixos[:2], df)
            palpites.append(sorted(aposta[:15]))
        return jsonify({'palpites': palpites})
    except Exception as e:
        print(f"Erro ao gerar palpites: {str(e)}", file=sys.stderr)
        return jsonify({'erro': 'Falha ao gerar palpites'}), 500

@app.route('/historico', methods=['GET'])
def historico():
    try:
        sorteios = df.to_dict('records')
        return jsonify({'sorteios': sorteios})
    except Exception as e:
        print(f"Erro ao carregar histórico: {str(e)}", file=sys.stderr)
        return jsonify({'erro': 'Falha ao carregar histórico'}), 500

@app.route('/taxas_acerto', methods=['GET'])
def taxas_acerto():
    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'erro': 'Login necessário'}), 401
        decoded_token = auth.verify_id_token(token.split('Bearer ')[1])
        user_name = decoded_token.get('name', 'Usuário')
        taxas = calcular_taxas_acerto(df)
        return jsonify({'user_name': user_name, 'taxas': taxas})
    except Exception as e:
        print(f"Erro ao verificar token: {str(e)}", file=sys.stderr)
        return jsonify({'erro': 'Token inválido'}), 401

if __name__ == '__main__':
    try:
        port = int(os.getenv('PORT', 10000))
        print(f"Iniciando Flask na porta {port}...", file=sys.stderr)
        app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as e:
        print(f"Erro ao iniciar Flask: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        raise
