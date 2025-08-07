from flask import request, jsonify
from auth_middleware import verificar_token
from firestore_utils import salvar_aposta, obter_apostas

@app.route('/salvar_aposta', methods=['POST'])
@verificar_token
def salvar_aposta_route():
    data = request.get_json()
    uid = request.uid
    numeros = data.get('numeros')
    concurso = data.get('concurso')
    if not numeros or not concurso:
        return jsonify({'error': 'Dados incompletos'}), 400
    salvar_aposta(uid, numeros, concurso)
    return jsonify({'status': 'Aposta salva com sucesso'})

@app.route('/minhas_apostas', methods=['GET'])
@verificar_token
def minhas_apostas():
    uid = request.uid
    apostas = obter_apostas(uid)
    return jsonify({'apostas': apostas})