from flask import Blueprint, jsonify
from services.estatisticas_service import gerar_estatisticas

estatisticas_bp = Blueprint('estatisticas', __name__)

@estatisticas_bp.route('/estatisticas', methods=['GET'])
def estatisticas():
    try:
        resultado = gerar_estatisticas()
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
