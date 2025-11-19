import requests
from collections import Counter

class EstatisticasService:

    def __init__(self):
        self.API_URL = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil"  # API oficial da Caixa

    def obter_ultimos_concursos(self, quantidade=50):
        concursos = []

        try:
            for i in range(quantidade):
                concurso_num = "latest" if i == 0 else f"latest-{i}"
                url = f"{self.API_URL}/{concurso_num}"
                response = requests.get(url, verify=False, timeout=5)

                if response.status_code == 200:
                    data = response.json()
                    concursos.append(data)
                else:
                    break

        except Exception as erro:
            print(f"Erro ao consultar API: {erro}")

        return concursos

    def calcular_estatisticas(self, concursos):
        dezenas = []

        for c in concursos:
            dezenas.extend(list(map(int, c["listaDezenas"])) )

        contagem = Counter(dezenas)

        mais_frequentes = contagem.most_common(10)
        menos_frequentes = contagem.most_common()[-10:]

        media_soma = sum(map(sum, [list(map(int, c["listaDezenas"])) for c in concursos])) / len(concursos)

        return {
            "total_concursos": len(concursos),
            "mais_frequentes": mais_frequentes,
            "menos_frequentes": menos_frequentes,
            "media_soma": media_soma
        }

    def gerar_estatisticas(self):
        concursos = self.obter_ultimos_concursos(60)  # usa últimos 60 concursos
        if not concursos:
            return {"erro": "Não foi possível obter dados da API"}

        return self.calcular_estatisticas(concursos)
