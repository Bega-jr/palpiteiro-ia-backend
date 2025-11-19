from flask import Flask, jsonify
from flask_cors import CORS

# Inicializa o Flask
app = Flask(__name__)
CORS(app)

# =========================
# Importa as rotas
# =========================
# IMPORTANTE:
# Essas importações PRECISAM vir após a criação do "app"
# pois cada arquivo de rota vai usar o "app" declarado acima.

from routes.estatisticas_routes import *
from routes.apostas_routes import *

# =========================
# Rota raiz / status
# =========================
@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "Backend Palpiteiro IA rodando!"})

# =========================
# Executar localmente
# =========================
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
