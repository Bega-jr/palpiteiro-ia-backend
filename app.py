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

# 4. Exemplo de Rota (Sua Rota de Teste)
# Se você estiver usando o endpoint '/apostas/gerar' no seu frontend:
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

# 5. Rota Raiz (Health Check)
@app.route('/', methods=['GET', 'HEAD'])
def health_check():
    """ Rota de verificação de saúde usada pelo Render. """
    return jsonify({"status": "ok"}), 200

# 6. Inicialização (se estiver usando o servidor de desenvolvimento local)
if __name__ == '__main__':
    # A porta 5000 é a porta padrão para o Render, mas certifique-se de que
    # o Gunicorn/Render está configurado para usá-la em produção.
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))
