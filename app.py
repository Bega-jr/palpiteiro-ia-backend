from flask import Flask, jsonify
from flask_cors import CORS

# Rotas
from routes.estatisticas_route import estatisticas_bp
from routes.apostas_route import apostas_bp

app = Flask(__name__)
CORS(app)


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Backend Palpiteiro IA rodando!"})


# Registrar rotas
app.register_blueprint(estatisticas_bp)
app.register_blueprint(apostas_bp)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
