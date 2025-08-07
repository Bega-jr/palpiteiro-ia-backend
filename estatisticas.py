@app.route('/estatisticas', methods=['GET'])
def estatisticas():
    global df
    try:
        numeros = []
        for i in range(1, 16):
            coluna = f'bola_{i}'
            numeros.extend(df[coluna].dropna().astype(int).tolist())

        from collections import Counter
        contagem = Counter(numeros)
        mais_frequentes = sorted(contagem.items(), key=lambda x: -x[1])[:5]
        menos_frequentes = sorted(contagem.items(), key=lambda x: x[1])[:5]
        media_soma = round(df[[f'bola_{i}' for i in range(1, 16)]].astype(float).sum(axis=1).mean(), 2)

        return jsonify({
            'mais_frequentes': mais_frequentes,
            'menos_frequentes': menos_frequentes,
            'media_soma': media_soma
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500