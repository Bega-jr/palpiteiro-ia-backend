README - Backend pronto para Render
----------------------------------

1) Estrutura esperada (no repo):
   - app.py
   - requirements.txt
   - Dockerfile
   - services/firestore_utils.py
   - historico_lotofacil.csv  (coloque na raiz do repo ou ajuste CSV_PATH env var)

2) No Render (painel do serviço):
   - Vá em Environment -> Secret Files -> Upload File
     Nome do arquivo no Render: firebase-adminsdk.json
   - Vá em Environment -> Environment Variables -> Add
     Name: GOOGLE_APPLICATION_CREDENTIALS
     Value: /etc/secrets/firebase-adminsdk.json

3) Faça deploy (se usar Docker, Render utilizará o Dockerfile).

4) Health check:
   - Acesse: https://<seu-servico>.onrender.com/health
   - Deve retornar JSON com "firebase_connected": true

5) Segurança:
   - NUNCA suba o arquivo JSON do Firebase no repositório público.
   - Use Secret Files do Render ou variáveis de ambiente seguras.