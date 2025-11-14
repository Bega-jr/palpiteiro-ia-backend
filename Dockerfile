# ---------- Build ----------
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ---------- Runtime ----------
FROM python:3.11-slim
WORKDIR /app

# Copia apenas binários
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Código essencial
COPY app.py auth_middleware.py estatisticas.py firestore_utils.py ./
COPY historico_lotofacil.csv aposta_semanal.json ./

# Segurança: remove arquivos sensíveis
RUN rm -f firebase-adminsdk.json

ENV PYTHONUNBUFFERED=1 \
    PORT=5000

EXPOSE $PORT

CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "--timeout", "120", "--preload", "app:app"]
