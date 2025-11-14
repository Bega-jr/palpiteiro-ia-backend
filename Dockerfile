FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY app.py auth_middleware.py firestore_utils.py ./

ENV PYTHONUNBUFFERED=1 PORT=5000
EXPOSE $PORT
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "--timeout", "120", "--preload", "app:app"]
