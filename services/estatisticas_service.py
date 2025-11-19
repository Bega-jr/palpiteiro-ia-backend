import pandas as pd
from collections import Counter

df = pd.read_csv("historico_lotofacil.csv")

def gerar_estatisticas():
    numeros = []

    # Carregando bolas
    for i in range(1, 16):
        coluna = f'bola_{i}'
        numeros.extend(df[coluna].dropna().astype(int).tolist())

    contagem = Counter(numeros)

    mais_frequentes = sorted(contagem.items(), key=lambda x: -x[1])[:5]
    menos_frequentes = sorted(contagem.items(), key=lambda x: x[1])[:5]

    media_soma = round(
        df[[f'bola_{i}' for i in range(1, 16)]].astype(float).sum(axis=1).mean(), 2
    )

    return {
        "mais_frequentes": mais_frequentes,
        "menos_frequentes": menos_frequentes,
        "media_soma": media_soma
    }
