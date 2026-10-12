import os

# Segredos vem do ambiente, nunca do codigo. Os padroes abaixo servem so para
# desenvolvimento local e para a suite de testes; em qualquer outro ambiente,
# defina INTERNAL_TOKEN e ADMIN_TOKEN no docker-compose ou no .env.
INTERNAL_TOKEN = os.environ.get("INTERNAL_TOKEN", "dev-internal-token")
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "dev-admin-token")

# Origens do front-end autorizadas a chamar a API pelo navegador (CORS)
ALLOWED_ORIGINS = [o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "*").split(",") if o.strip()]

# Rotas que nao exigem INTERNAL-TOKEN nem entram no log: o Docker consulta
# o /health a cada poucos segundos.
BYPASS_ENDPOINTS = {"/health"}

INTERNAL_TOKEN_HEADER = "INTERNAL-TOKEN"
ADMIN_TOKEN_HEADER = "ADMIN-TOKEN"
PAYER_TOKEN_HEADER = "PAYER-TOKEN"
REQUEST_ID_HEADER = "X-Request-Id"
