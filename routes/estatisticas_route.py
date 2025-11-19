from flask import Blueprint, jsonify
from services.estatisticas_service import EstatisticasService

estatisticas_bp = Blueprint("estatisticas_bp", __name__)
service = EstatisticasService()

@estatisticas_bp.route("/estatisticas", methods=["GET"])
def estatisticas():
    resultado = service.gerar_estatisticas()
    return jsonify(resultado)
