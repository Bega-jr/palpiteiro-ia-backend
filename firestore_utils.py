import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

# Usa ENV VAR como JSON string
service_account_json = os.getenv('FIREBASE_SERVICE_ACCOUNT')

if service_account_json and not firebase_admin._apps:
    cred_dict = json.loads(service_account_json)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

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
