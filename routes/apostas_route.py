from flask import Blueprint, jsonify
import random
import requests

apostas_bp = Blueprint("apostas", __name__)

API_ESTATISTICAS = "http://localhost:5000/estatisticas"


def gerar_aposta(numeros_base, tamanho=15):
    aposta = set()

    # Começa com os mais frequentes
    for n in numeros_base:
        if len(aposta) < tamanho:
            aposta.add(n)

    # Completa com números aleatórios de 1 a 25
    while len(aposta) < tamanho:
        aposta.add(random.randint(1, 25))

    return sorted(list(aposta))


@apostas_bp.route("/gerar-apostas", methods=["GET"])
def gerar_apostas():
    try:
        # Consulta estatísticas dinâmicas
        response = requests.get(API_ESTATISTICAS)
        dados = response.json()

        mais = [n[0] for n in dados["mais_frequentes"]]
        menos = [n[0] for n in dados["menos_frequentes"]]

        apostas = []

        # 5 apostas usando números mais frequentes
        for _ in range(5):
            apostas.append(gerar_aposta(mais))

        # 2 apostas usando os menos frequentes
        for _ in range(2):
            apostas.append(gerar_aposta(menos))

        return jsonify({
            "total": len(apostas),
            "apostas": apostas
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
