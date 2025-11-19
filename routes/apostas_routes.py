from flask import Blueprint, request, jsonify
from services.apostas_service import gerar_apostas

apostas_bp = Blueprint('apostas', __name__)

@apostas_bp.route("/", methods=["GET"])
def listar_apostas():
    return jsonify({"message": "Rotas de apostas funcionando!"})

# Nova rota de geração de palpites
@apostas_bp.route("/gerar_palpites", methods=["GET"])
def gerar_palpites_route():
    try:
        tipo = request.args.get("tipo", "aleatorio")
        jogos = gerar_apostas(tipo)
        return jsonify({"palpites": jogos})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
