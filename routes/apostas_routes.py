from flask import request, jsonify
from app import app
from services.apostas_service import gerar_apostas

@app.route('/gerar_palpites', methods=['GET'])
def gerar_palpites():
    try:
        tipo = request.args.get("tipo", "aleatorio")
        jogos = gerar_apostas(tipo)
        return jsonify({"palpites": jogos})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
