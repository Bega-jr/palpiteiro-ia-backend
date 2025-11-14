FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# COPIE OS ARQUIVOS
COPY app.py auth_middleware.py firestore_utils.py ./

# NÃO DEFINA PORT AQUI
ENV PYTHONUNBUFFERED=1

# USE $PORT DO RENDER
EXPOSE $PORT
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "--timeout", "120", "--preload", "app:app"]
