import os
import logging
import firebase_admin
from firebase_admin import credentials, firestore

# Caminho do arquivo de credenciais no Render
FIREBASE_CRED_PATH = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS",
    "/etc/secrets/firebase-adminsdk.json"
)

# Inicializa Firebase Admin
firebase_initialized = False
db = None

try:
    cred = credentials.Certificate(FIREBASE_CRED_PATH)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    firebase_initialized = True
    logging.info("Firebase Admin inicializado com sucesso.")
except Exception as e:
    logging.warning(f"Falha ao inicializar Firebase Admin: {e}")


# -------------------------------
# FUNÇÃO SALVAR APOSTA
# -------------------------------
def salvar_aposta(aposta):
    if not firebase_initialized:
        raise Exception("Firebase não inicializado.")

    doc_ref = db.collection("apostas").document()
    doc_ref.set(aposta)
    return True


# -------------------------------
# FUNÇÃO CARREGAR APOSTAS
# -------------------------------
def carregar_apostas():
    if not firebase_initialized:
        raise Exception("Firebase não inicializado.")

    docs = db.collection("apostas").stream()
    return [doc.to_dict() for doc in docs]
