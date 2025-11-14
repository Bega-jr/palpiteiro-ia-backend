import firebase_admin
from firebase_admin import credentials, firestore
import os

# Usa o Secret File do Render
if not firebase_admin._apps:
    cred_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '/app/firebase-adminsdk.json')
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    else:
        firebase_admin.initialize_app()  # Fallback

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
