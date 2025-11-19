import random
from services.estatisticas_service import carregar_estatisticas


# --------------------------------------------------------
# Função auxiliar para gerar um jogo simples de 15 números
# --------------------------------------------------------
def gerar_jogo(numeros_possiveis):
    return sorted(random.sample(numeros_possiveis, 15))


# --------------------------------------------------------
# Gera apostas utilizando estatísticas dinâmicas
# tipo = aleatorio | premium
# --------------------------------------------------------
def gerar_apostas(tipo="aleatorio"):
    stats = carregar_estatisticas()

    mais_freq = [n for n, _ in stats["mais_frequentes"]]
    menos_freq = [n for n, _ in stats["menos_frequentes"]]

    apostas = []

    # ==================================================================
    # 1. MODO ALEATÓRIO
    # ==================================================================
    if tipo == "aleatorio":
        for _ in range(5):
            jogo = gerar_jogo(list(range(1, 26)))
            apostas.append(jogo)
        return apostas

    # ==================================================================
    # 2. MODO PREMIUM (melhor combinação das estatísticas)
    # ==================================================================
    elif tipo == "premium":

        # 1) Jogos baseados nos números mais frequentes
        for _ in range(2):
            base = set(mais_freq)
            resto = [n for n in range(1, 26) if n not in base]
            faltam = 15 - len(base)
            jogo = sorted(list(base) + random.sample(resto, faltam))
            apostas.append(jogo)

        # 2) Jogos misturados (meio termo)
        for _ in range(3):
            base = random.sample(mais_freq, 3) + random.sample(menos_freq, 3)
            base = list(set(base))[:6]
            resto = [n for n in range(1, 26) if n not in base]
            faltam = 15 - len(base)
            jogo = sorted(base + random.sample(resto, faltam))
            apostas.append(jogo)

        # 3) Jogos baseados nos menos frequentes
        for _ in range(2):
            base = set(menos_freq)
            resto = [n for n in range(1, 26) if n not in base]
            faltam = 15 - len(base)
            jogo = sorted(list(base) + random.sample(resto, faltam))
            apostas.append(jogo)

        return apostas

    # ==================================================================
    # Caso tipo inválido
    # ==================================================================
    else:
        return {"erro": "Tipo inválido. Use aleatorio ou premium"}
