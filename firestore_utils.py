import firebase_admin
from firebase_admin import firestore
import os

# Usa Application Default Credentials (ADC) — Render + Google Cloud
if not firebase_admin._apps:
    firebase_admin.initialize_app()

db = firestore.client()

def salvar_aposta(uid, numeros, concurso):
    doc_ref = db.collection('usuarios').document(uid).collection('apostas').document(str(concurso))
    doc_ref.set({
        'numeros': numeros,
        'concurso': concurso,
        'timestamp': firestore.SERVER_TIMESTAMP
    }, merge=True)

def obter_apostas(uid):
    apostas_ref = db.collection('usuarios').document(uid).collection('apostas')
    docs = apostas_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).stream()
    return [{**doc.to_dict(), 'id': doc.id} for doc in docs]
def obter_apostas(uid):
    apostas_ref = db.collection('usuarios').document(uid).collection('apostas')
    docs = apostas_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).stream()
    return [{**doc.to_dict(), 'id': doc.id} for doc in docs]
