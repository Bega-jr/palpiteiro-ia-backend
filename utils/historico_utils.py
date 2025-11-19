import pandas as pd

def carregar_historico(caminho="historico_lotofacil.csv"):
    return pd.read_csv(caminho)
