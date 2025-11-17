import os
import logging
from firebase_admin import credentials, firestore, initialize_app, auth

logger = logging.getLogger("firestore_utils")

FIREBASE_CRED_PATH = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "/mnt/data/firebase-adminsdk.json")

if not firestore._apps:
    try:
        cred = credentials.Certificate(FIREBASE_CRED_PATH)
        initialize_app(cred)
        logger.info("Firebase initialized in firestore_utils")
    except Exception as e:
        logger.warning("Firebase init failed in firestore_utils: %s", e)

def salvar_aposta(uid, numeros, concurso=None):
    db = firestore.client()
    doc_ref = db.collection("usuarios").document(uid).collection("apostas").document(concurso or "aposta_"+str(int(datetime.utcnow().timestamp())))
    doc_ref.set({
        "numeros": numeros,
        "concurso": concurso,
        "timestamp": firestore.SERVER_TIMESTAMP
    })
    return True

def obter_apostas(uid, limit=50):
    db = firestore.client()
    apostas_ref = db.collection("usuarios").document(uid).collection("apostas").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(limit)
    docs = apostas_ref.stream()
    result = []
    for doc in docs:
        d = doc.to_dict()
        d["id"] = doc.id
        result.append(d)
    return result