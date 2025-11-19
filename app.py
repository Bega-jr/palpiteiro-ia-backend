from flask import Flask, jsonify
from flask_cors import CORS
from estatisticas import estatisticas   # importa a função corretamente

app = Flask(__name__)
CORS(app)

# registra o endpoint /estatisticas
app.add_url_rule('/estatisticas', 'estatisticas', estatisticas)


@app.route('/')
def home():
    return jsonify({
        "status": "VERDE TOTAL",
        "message": "Palpiteiro IA backend 100% FUNCIONANDO – sem Firebase, sem erro, sem nada!"
    })


@app.route('/historico')
def historico():
    return jsonify({
        "sorteios": [{
            "concurso": "3538",
            "data": "18/11/2025",
            "numeros": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
        }]
    })


@app.route('/gerar_palpites')
def gerar_palpites():
    import random
    numeros = sorted(random.sample(range(1, 26), 15))
    return jsonify({"palpites": [numeros]})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
