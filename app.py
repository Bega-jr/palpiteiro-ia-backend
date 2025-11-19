import pandas as pd
from collections import Counter
from flask import jsonify

# Carrega o arquivo CSV ao iniciar o servidor
df = pd.read_csv("historico_lotofacil.csv")

@app.route('/estatisticas', methods=['GET'])
def obter_estatisticas():
    try:
        numeros = []
        
        # Carrega todas as bolas do histórico
        for i in range(1, 16):
            coluna = f'bola_{i}'
            numeros.extend(df[coluna].dropna().astype(int).tolist())

        # Frequência dos números
        contagem = Counter(numeros)

        mais_frequentes = sorted(contagem.items(), key=lambda x: -x[1])[:5]
        menos_frequentes = sorted(contagem.items(), key=lambda x: x[1])[:5]

        media_soma = round(
            df[[f'bola_{i}' for i in range(1, 16)]]
            .astype(float)
            .sum(axis=1)
            .mean(),
            2
        )

        return jsonify({
            'mais_frequentes': mais_frequentes,
            'menos_frequentes': menos_frequentes,
            'media_soma': media_soma
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
