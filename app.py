from flask import Flask
from flask_cors import CORS

from routes.estatisticas_routes import estatisticas_bp
from routes.apostas_routes import apostas_bp

app = Flask(__name__)
CORS(app)

# Registrar blueprints
app.register_blueprint(estatisticas_bp, url_prefix='/estatisticas')
app.register_blueprint(apostas_bp, url_prefix='/apostas')

@app.route("/health")
def health():
    return {"status": "ok"}, 200

@app.route("/")
def home():
    return {"message": "Palpiteiro IA Backend - OK!"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
