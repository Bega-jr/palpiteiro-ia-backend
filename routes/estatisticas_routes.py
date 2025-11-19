from flask import Blueprint, jsonify
from services.estatisticas_service import EstatisticasService

# Nome simples do blueprint
estatisticas_bp = Blueprint("estatisticas", __name__)
service = EstatisticasService()

@estatisticas_bp.route("/", methods=["GET"])
def estatisticas():
    resultado = service.gerar_estatisticas()
    return jsonify(resultado)
