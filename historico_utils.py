import requests
from firebase_admin import firestore

db = firestore.client()

def atualizar_historico():
    """
    Baixa o último sorteio da API externa e grava no Firestore
    apenas se ainda não existir.
    """
    try:
        url = "https://api.guidi.dev.br/loteria/lotofacil/ultimo"
        r = requests.get(url, timeout=10)
        data = r.json()

        concurso = str(data.get("concurso"))
        numeros = data.get("numeros", [])
        data_sorteio = data.get("data")

        doc_ref = db.collection("historico").document(concurso)
        if not doc_ref.get().exists:
            doc_ref.set({
                "concurso": concurso,
                "data": data_sorteio,
                "numeros": numeros
            })
            return True  # novo registro
        return False  # já existia

    except Exception as e:
        print("Erro ao atualizar histórico:", e)
        return False


def carregar_historico():
    """
    Retorna todos os concursos já salvos no Firestore.
    """
    docs = db.collection("historico").stream()
    lista = [doc.to_dict() for doc in docs]
    return lista
