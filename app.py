import os
import random
import requests
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from firebase_admin import credentials, firestore, initialize_app, auth as fb_auth

app = Flask(__name__)
CORS(app)

# ---------- FIREBASE ----------
# Render Secret File (caminho oficial 2025)
cred = credentials.Certificate("/etc/secrets/firebase-adminsdk.json")
initialize_app(cred)
db = firestore.client()

# ---------- AUTH ----------
def verify_token(f):
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization", "")
        if not token.startswith("Bearer "):
            return jsonify({"error": "Token ausente"}), 401
        try:
            decoded = fb_auth.verify_id_token(token.split("Bearer ")[1])
            request.uid = decoded["uid"]
            return f(*args, **kwargs)
        except:
            return jsonify({"error": "Token inválido"}), 401
    wrapper.__name__ = f.__name__
    return wrapper

# ---------- PALPITES ----------
FIXED_NUMBERS = [1, 3, 4, 15, 21, 23]

@app.route("/gerar_palpites", methods=["GET"])
@verify_token
def gerar_palpites():
    tipo = request.args.get("tipo", "aleatorio").lower()
    uid = request.uid

    if tipo == "premium":
        palpites = [sorted(FIXED_NUMBERS + random.sample([n for n in range(1,26) if n not in FIXED_NUMBERS], 9)) for _ in range(7)]
    elif tipo == "fixo":
        palpites = [sorted(FIXED_NUMBERS + random.sample([n for n in range(1,26) if n not in FIXED_NUMBERS], 9))]
    else:
        palpites = [sorted(random.sample(range(1, 26), 15))]

    # Salva todas as apostas no Firestore
    for palpite in palpites:
        db.collection("usuarios").document(uid).collection("apostas").add({
            "numeros": palpite,
            "tipo": tipo,
            "timestamp": firestore.SERVER_TIMESTAMP
        })

    return jsonify({"palpites": palpites})

@app.route("/historico")
def historico():
    try:
        r = requests.get("https://api.guidi.dev.br/loteria/lotofacil/ultimo", timeout=10)
        data = r.json()
        return jsonify({"sorteios": [data]})
    except:
        return jsonify({"sorteios": []})

@app.route("/minhas_apostas")
@verify_token
def minhas_apostas():
    uid = request.uid
    docs = db.collection("usuarios").document(uid).collection("apostas")\
        .order_by("timestamp", direction=firestore.Query.DESCENDING).limit(50).stream()
    apostas = [doc.to_dict() for doc in docs]
    return jsonify({"apostas": apostas})

@app.route("/")
def home():
    return jsonify({"status": "ok", "message": "Palpiteiro IA v2 – VERDE E FUNCIONANDO!"})

import stripe
stripe.api_key = "sk_test_51...SUA_CHAVE_SECRETA_STRIPE"  # depois coloca em env var

@app.route("/create-checkout-session", methods=["POST"])
@verify_token_required
def create_checkout():
    session = stripe.checkout.Session.create(
        payment_method_types=["card", "pix"],
        line_items=[{
            "price": "price_1...SEU_PRICE_ID_R$9,90",  # cria no dashboard Stripe
            "quantity": 1,
        }],
        mode="subscription",
        success_url="https://palpiteiro-ia.netlify.app/sucesso",
        cancel_url="https://palpiteiro-ia.netlify.app",
        client_reference_id=request.uid,
    )
    return jsonify({"id": session.id})

@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, "whsec_...SEU_WEBHOOK_SECRET")
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            if session.payment_status == "paid":
                uid = session.client_reference_id
                db.collection("usuarios").document(uid).set({"premium": True}, merge=True)
    except:
        return "", 400
    return "", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
