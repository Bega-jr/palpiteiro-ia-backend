from flask import Flask, jsonify, request
from flask_cors import CORS # 1. Importa a extensão CORS
import os
import random
# Adicione outras importações do seu projeto (e.g., Firebase Admin SDK, etc.)

# 2. Inicialização do Flask
app = Flask(__name__)

# 3. Configuração CRÍTICA do CORS
# Permitimos todas as origens ('*') por enquanto para o desenvolvimento
# Se você tiver a URL exata do Codespace, pode usá-la.
CORS(app) 

# 4. Rota de Geração de Apostas
@app.route('/apostas/gerar', methods=['GET'])
def gerar_apostas():
    """
    Simula a geração de apostas Lotofácil.
    Endpoint: /apostas/gerar?tipo=aleatorio
    """
    tipo = request.args.get('tipo', 'aleatorio')
    
    # 🚨 NOTA: Você deve implementar sua lógica de autenticação Firebase aqui
    # e sua lógica de geração de números.
    
    # Simulação de dados: Retorna 3 jogos de 15 números
    apostas_simuladas = []
    for _ in range(3):
        aposta = sorted(random.sample(range(1, 26), 15))
        apostas_simuladas.append(aposta)
        
    print(f"Gerando apostas tipo: {tipo}")
    
    return jsonify({
        "status": "sucesso",
        "tipo": tipo,
        "apostas": apostas_simuladas
    })

# 5. Rota de Estatísticas (Placeholder)
@app.route('/estatisticas', methods=['GET'])
def get_estatisticas():
    """
    Placeholder para a rota de estatísticas, aceita GET.
    Isto resolve o erro 404 do preflight.
    """
    # Dados simulados para que o frontend não quebre
    dados_simulados = {
        "mais_sorteados": [3, 15, 20, 1, 13],
        "menos_sorteados": [2, 24, 18, 17, 7],
        "frequencia": {
            "1": 0.85, "2": 0.55, "3": 0.92, 
            "24": 0.45, "25": 0.78
        }
    }
    return jsonify(dados_simulados)

# 6. Rota de Histórico (Placeholder)
@app.route('/historico', methods=['GET'])
def get_historico():
    """
    Placeholder para a rota de histórico, aceita GET.
    Isto resolve o erro 404 do preflight.
    """
    # Retorna uma lista vazia de jogos por padrão
    return jsonify({"jogos": []})


# 7. Rota Raiz (Health Check)
@app.route('/', methods=['GET', 'HEAD'])
def health_check():
    """ Rota de verificação de saúde usada pelo Render. """
    return jsonify({"status": "ok"}), 200

# 8. Inicialização (se estiver usando o servidor de desenvolvimento local)
if __name__ == '__main__':
    # A porta 5000 é a porta padrão para o Render, mas certifique-se de que
    # o Gunicorn/Render está configurado para usá-la em produção.
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))
