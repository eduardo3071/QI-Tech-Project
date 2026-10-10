# Antecipa Saúde

Conta e antecipação de recebíveis de convênio para clínicas, consultórios e laboratórios. A clínica registra o valor que a operadora deve, antecipa esse valor descontado de uma tarifa e, quando a operadora paga, o ciclo fecha. A conta também transfere dinheiro para outras contas da plataforma, com tarifa.

Projeto do Bootcamp QI Tech 2026: API REST em Python + FastAPI + SQLAlchemy sobre PostgreSQL, tudo em Docker. O desenho completo e as decisões estão na RFC (`docs/RFC.md`).

## Como rodar

Pré-requisito: Docker com o plugin `docker compose`.

```bash
# sobe a API (porta 8000) e o banco
docker compose up --build

# roda a suíte de testes num banco descartável, criado pelo mesmo database/database.sql
docker compose --profile test run --rm tests
```

`database/database.sql` é a fonte de verdade do schema e roda só quando o volume do banco nasce. Se o arquivo mudar, recrie o volume: `docker compose down -v && docker compose up --build`.

Os testes são de caixa-preta: falam com a API só por HTTP, sem importar nada de `src/`. Para rodar fora do Docker contra uma API já de pé:

```bash
pip install -r requirements.txt
API_URL=http://localhost:8000 pytest -q
```

## Rotas

Recurso no singular, em inglês, identificado pela `_key` (UUID). Valores em centavos, inteiros. Todo erro volta com `title`, `description`, `translation` e `code`.

| Método | Caminho | O que faz |
|---|---|---|
| `GET` | `/health` | API e banco de pé |
| `POST` | `/client` | Cadastra a clínica (CNPJ único) |
| `POST` | `/client/{client_key}/account` | Abre uma conta `ACTIVE` |
| `GET` | `/account/{account_key}` | Lê a conta |
| `PATCH` | `/account/{account_key}` | Muda o estado: `ACTIVE`, `BLOCKED`, `CLOSED` (final) |
| `POST` | `/account/{account_key}/transaction` | Transferência para outra conta, tarifa de R$ 2,00, idempotente por `idempotency_key` |
| `GET` | `/account/{account_key}/transactions?page=&limit=` | Extrato paginado com o saldo |
| `POST` | `/payer` | Cadastra a operadora |
| `POST` | `/account/{account_key}/receivable` | Registra um recebível (`external_id` único por operadora) |
| `GET` | `/receivable/{receivable_key}` | Lê o recebível |
| `POST` | `/receivable/{receivable_key}/advance` | Antecipa o recebível |
| `POST` | `/receivable/{receivable_key}/settlement` | Registra o pagamento da operadora (idempotente) |

## Exemplo rápido

```bash
CLIENT=$(curl -s -X POST localhost:8000/client -H 'Content-Type: application/json' \
  -d '{"legal_name":"Clinica Sao Lucas","document_number":"12345678000190","email":"fin@saolucas.com"}' | jq -r .client_key)
ACCOUNT=$(curl -s -X POST localhost:8000/client/$CLIENT/account | jq -r .account_key)
PAYER=$(curl -s -X POST localhost:8000/payer -H 'Content-Type: application/json' \
  -d '{"legal_name":"Operadora X","document_number":"98765432000110"}' | jq -r .payer_key)
REC=$(curl -s -X POST localhost:8000/account/$ACCOUNT/receivable -H 'Content-Type: application/json' \
  -d "{\"payer_key\":\"$PAYER\",\"external_id\":\"GUIA-0001\",\"gross_amount\":100000,\"due_date\":\"2026-12-31\"}" | jq -r .receivable_key)
curl -s -X POST localhost:8000/receivable/$REC/advance
curl -s "localhost:8000/account/$ACCOUNT/transactions?limit=20"
```

## Estrutura

```
src/
  app.py          rotas e tradução de erros
  resources/      entrada e saída HTTP
  schemas/        contrato de entrada (Pydantic, campos extras recusados)
  controllers/    regras de negócio e commit
  repositories/   única camada que fala com o banco
  models/         espelho das tabelas
  dtos/           o que sai na resposta
  errors/         erros de negócio com status e código
database/
  database.sql    schema (fonte de verdade)
  er_diagram.mmd  diagrama entidade-relacionamento
tests/            testes de caixa-preta por HTTP
docs/             RFC
```
