from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import random

app = Flask(__name__)
CORS(app)

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

if __name__ == '__main__':
    app.run(debug=True)
