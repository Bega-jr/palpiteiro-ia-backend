from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
from collections import Counter

# Inicializa o Flask
app = Flask(__name__)
CORS(app)

# Carrega o histórico na inicialização do servidor
df = pd.read_csv("historico_lotofacil.csv")

@app.route('/estatisticas', methods=['GET'])
def obter_estatisticas():
    """Retorna estatísticas gerais da Lotofácil com base no histórico."""
    try:
        numeros = []

        # Carrega todas as bolas do histórico
        for i in range(1, 16):
            coluna = f'bola_{i}'
            numeros.extend(
                df[coluna].dropna().astype(int).tolist()
            )

        # Frequência dos números
        contagem = Counter(numeros)

        mais_frequentes = sorted(contagem.items(), key=lambda x: -x[1])[:5]
        menos_frequentes = sorted(contagem.items(), key=lambda x: x[1])[:5]

        # Média das somas dos jogos
        media_soma = round(
            df[[f'bola_{i}' for i in range(1, 16)]]
            .astype(float)
            .sum(axis=1)
            .mean(),
            2
        )

        return jsonify({
            "mais_frequentes": mais_frequentes,
            "menos_frequentes": menos_frequentes,
            "media_soma": media_soma
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Rota simples para teste
@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "API Lotofacil backend funcionando!"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
