from flask import Flask, jsonify
from flask_cors import CORS

from routes.estatisticas_route import estatisticas_bp

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Registrar rotas
    app.register_blueprint(estatisticas_bp)

    @app.route('/', methods=['GET'])
    def home():
        return jsonify({"status": "Backend Palpiteiro IA rodando!"})

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
