from flask import Flask, jsonify
from flask_cors import CORS

# Rotas
from routes.estatisticas_route import estatisticas_bp

app = Flask(__name__)
CORS(app)


# Rota padrão apenas para teste
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Backend Palpiteiro IA rodando!"})


# Registrar as rotas
app.register_blueprint(estatisticas_bp)


if __name__ == "__main__":
    # Necessário para rodar no GitHub Codespaces
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
