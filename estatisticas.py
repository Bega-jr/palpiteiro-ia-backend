from flask import jsonify
from collections import Counter
from historico_utils import carregar_historico

def estatisticas():
    try:
        dados = carregar_historico()
        if not dados:
            return jsonify({"error": "Sem dados suficientes"}), 400

        # junta tudo
        numeros = []
        somas = []
        for concurso in dados:
            nums = concurso["numeros"]
            numeros.extend(nums)
            somas.append(sum(nums))

        contagem = Counter(numeros)

        mais_frequentes = contagem.most_common(5)
        menos_frequentes = sorted(contagem.items(), key=lambda x: x[1])[:5]
        media_soma = round(sum(somas) / len(somas), 2)

        return jsonify({
            "mais_frequentes": mais_frequentes,
            "menos_frequentes": menos_frequentes,
            "media_soma": media_soma
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
