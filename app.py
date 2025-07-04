from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import random

app = Flask(__name__)
CORS(app)  # Permitir chamadas do frontend

# Carregar o histórico real dos sorteios a partir de um CSV com separador ';'
try:
    df = pd.read_csv("historico_lotofacil.csv", sep=";")
    df["numeros"] = df["numeros"].apply(lambda x: list(map(int, x.split(","))))
except Exception as e:
    df = pd.DataFrame(columns=["concurso", "data", "numeros"])
    print("Erro ao carregar o histórico:", e)

def escolher_fixos(df, n=4):
    frequencias = df['numeros'].explode().value_counts()
    return frequencias.head(n).index.tolist()

def gerar_aposta_diversa(fixos, df):
    frequencias = df['numeros'].explode().value_counts()
    frios = frequencias.tail(10).index.tolist()
    return sorted(fixos + random.sample([n for n in frios if n not in fixos], 11))

@app.route('/gerar_palpites', methods=['GET'])
def gerar_palpites():
    if df.empty:
        return jsonify({"erro": "Histórico indisponível"}), 500
    
    fixos = escolher_fixos(df)  # Ex.: [3, 15, 21, 23]
    palpites = []
    for i in range(7):
        if i < 5:  # Primeiras 5 apostas com números fixos
            aposta = fixos + random.sample([n for n in range(1, 26) if n not in fixos], 11)
        else:  # Últimas 2 apostas diversas
            aposta = gerar_aposta_diversa(fixos[:2], df)  # Menos fixos para diversidade
        palpites.append(sorted(aposta[:15]))
    return jsonify({'palpites': palpites})

@app.route('/historico', methods=['GET'])
def historico():
    if df.empty:
        return jsonify({"erro": "Nenhum sorteio encontrado"}), 500
    sorteios = df.to_dict('records')
    return jsonify({'sorteios': sorteios})

if __name__ == '__main__':
    app.run(debug=True)
