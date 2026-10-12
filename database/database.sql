-- QI Tech Bootcamp 2026 · Antecipa Saude
-- Banco de dados (PostgreSQL). Fonte de verdade do schema.
-- Roda uma vez, quando o volume do banco nasce: mudou este arquivo,
-- suba de novo com `docker compose down -v`.

-- =========================================================
-- client: a clinica, consultorio ou laboratorio
-- =========================================================
CREATE TABLE client (
    id              SERIAL PRIMARY KEY,                         -- interno: carrega a relacao
    client_key      CHAR(36)     NOT NULL UNIQUE,                -- externo: sai na URL
    legal_name      TEXT         NOT NULL,
    document_number CHAR(14)     NOT NULL UNIQUE,                -- CNPJ, sem mascara
    email           TEXT         NOT NULL,
    created_at      TIMESTAMP    NOT NULL DEFAULT now()
);

-- =========================================================
-- account_status: enumerador - onde uma conta pode estar
-- =========================================================
CREATE TABLE account_status (
    id          SERIAL PRIMARY KEY,
    enumerator  VARCHAR(20) NOT NULL UNIQUE                     -- ACTIVE | BLOCKED | CLOSED
);

-- =========================================================
-- account: a conta da clinica. O saldo mora numa coluna
-- (verdade do agora) e o extrato na tabela transaction.
-- Invariante: balance = soma de transaction.amount da conta.
-- =========================================================
CREATE TABLE account (
    id          SERIAL PRIMARY KEY,
    account_key CHAR(36)  NOT NULL UNIQUE,
    client_id   INTEGER   NOT NULL REFERENCES client(id),
    status_id   INTEGER   NOT NULL REFERENCES account_status(id),
    balance     BIGINT    NOT NULL DEFAULT 0,                   -- centavos, inteiro
    created_at  TIMESTAMP NOT NULL DEFAULT now(),
    updated_at  TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT balance_nao_negativo CHECK (balance >= 0)
);

-- =========================================================
-- account_status_event: uma linha por mudanca de estado da conta
-- =========================================================
CREATE TABLE account_status_event (
    id              SERIAL PRIMARY KEY,
    account_id      INTEGER   NOT NULL REFERENCES account(id),
    from_status_id  INTEGER   REFERENCES account_status(id),    -- nulo ao nascer
    to_status_id    INTEGER   NOT NULL REFERENCES account_status(id),
    reason          VARCHAR(255),
    created_at      TIMESTAMP NOT NULL DEFAULT now()
);

-- =========================================================
-- payer: a operadora/convenio devedora do recebivel. Cadastrada pelo
-- back-office; usa a propria credencial para avisar pagamentos.
-- =========================================================
CREATE TABLE payer (
    id              SERIAL PRIMARY KEY,
    payer_key       CHAR(36) NOT NULL UNIQUE,
    legal_name      TEXT     NOT NULL,
    document_number CHAR(14) NOT NULL UNIQUE,
    token_hash      CHAR(64) NOT NULL UNIQUE,                   -- SHA-256 da credencial; o token so aparece uma vez, no cadastro
    created_at      TIMESTAMP NOT NULL DEFAULT now()
);

-- =========================================================
-- receivable_status: enumerador - o ciclo de vida do recebivel
-- =========================================================
CREATE TABLE receivable_status (
    id          SERIAL PRIMARY KEY,
    enumerator  VARCHAR(20) NOT NULL UNIQUE                     -- PENDING | ADVANCED | SETTLED | LATE | DEFAULTED
);

-- =========================================================
-- receivable: o valor que a clinica tem a receber da operadora.
-- external_id e o numero da guia/fatura no sistema da operadora:
-- o mesmo credito nao entra duas vezes (nem em contas diferentes),
-- senao seria antecipado duas vezes.
-- =========================================================
CREATE TABLE receivable (
    id             SERIAL PRIMARY KEY,
    receivable_key CHAR(36)    NOT NULL UNIQUE,
    account_id     INTEGER     NOT NULL REFERENCES account(id),
    payer_id       INTEGER     NOT NULL REFERENCES payer(id),
    external_id    VARCHAR(64) NOT NULL,
    gross_amount   BIGINT      NOT NULL,                        -- centavos, o valor cheio do convenio
    due_date       DATE        NOT NULL,
    status_id      INTEGER     NOT NULL REFERENCES receivable_status(id),
    created_at     TIMESTAMP   NOT NULL DEFAULT now(),
    updated_at     TIMESTAMP   NOT NULL DEFAULT now(),
    CONSTRAINT gross_amount_positivo CHECK (gross_amount > 0),
    CONSTRAINT receivable_unico_por_operadora UNIQUE (payer_id, external_id)
);

-- =========================================================
-- receivable_status_event: uma linha por mudanca de estado
-- =========================================================
CREATE TABLE receivable_status_event (
    id              SERIAL PRIMARY KEY,
    receivable_id   INTEGER   NOT NULL REFERENCES receivable(id),
    from_status_id  INTEGER   REFERENCES receivable_status(id), -- nulo ao nascer (PENDING)
    to_status_id    INTEGER   NOT NULL REFERENCES receivable_status(id),
    reason          VARCHAR(255),
    created_at      TIMESTAMP NOT NULL DEFAULT now()
);

-- =========================================================
-- advance: a antecipacao - um recebivel so pode ser antecipado
-- uma vez (UNIQUE em receivable_id)
-- =========================================================
CREATE TABLE advance (
    id            SERIAL PRIMARY KEY,
    advance_key   CHAR(36)  NOT NULL UNIQUE,
    receivable_id INTEGER   NOT NULL REFERENCES receivable(id),
    fee_rate      NUMERIC(5,4) NOT NULL,                        -- ex.: 0.0350 = 3,5%
    fee_amount    BIGINT    NOT NULL,                           -- centavos
    net_amount    BIGINT    NOT NULL,                           -- centavos, o que cai na conta
    advanced_at   TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT advance_unico_por_recebivel UNIQUE (receivable_id),
    CONSTRAINT fee_amount_nao_negativo CHECK (fee_amount >= 0),
    CONSTRAINT net_amount_positivo CHECK (net_amount > 0)
);

-- =========================================================
-- transfer: transferencia entre contas da plataforma, com tarifa.
-- idempotency_key vem do cliente: repetir o mesmo pedido nao
-- movimenta dinheiro de novo.
-- =========================================================
CREATE TABLE transfer (
    id                     SERIAL PRIMARY KEY,
    transfer_key           CHAR(36)  NOT NULL UNIQUE,
    origin_account_id      INTEGER   NOT NULL REFERENCES account(id),
    destination_account_id INTEGER   NOT NULL REFERENCES account(id),
    amount                 BIGINT    NOT NULL,                  -- centavos, o que chega no destino
    fee_amount             BIGINT    NOT NULL,                  -- centavos, cobrado da origem
    idempotency_key        CHAR(36)  NOT NULL,
    created_at             TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT transfer_idempotente UNIQUE (origin_account_id, idempotency_key),
    CONSTRAINT transfer_contas_distintas CHECK (origin_account_id <> destination_account_id),
    CONSTRAINT transfer_amount_positivo CHECK (amount > 0),
    CONSTRAINT transfer_fee_nao_negativa CHECK (fee_amount >= 0)
);

-- =========================================================
-- transaction: o extrato. Toda movimentacao de conta, com sinal:
-- credito positivo, debito negativo. O banco recusa sinal trocado.
-- =========================================================
CREATE TABLE transaction (
    id              SERIAL PRIMARY KEY,
    transaction_key CHAR(36)    NOT NULL UNIQUE,
    account_id      INTEGER     NOT NULL REFERENCES account(id),
    receivable_id   INTEGER     REFERENCES receivable(id),      -- preenchido em antecipacao e liquidacao
    transfer_id     INTEGER     REFERENCES transfer(id),        -- preenchido em transferencia
    type            VARCHAR(20) NOT NULL,
    amount          BIGINT      NOT NULL,                       -- centavos; negativo em debito
    created_at      TIMESTAMP   NOT NULL DEFAULT now(),
    CONSTRAINT transaction_type_valido CHECK (
        type IN ('ADVANCE_CREDIT', 'SETTLEMENT_CREDIT', 'TRANSFER_IN', 'TRANSFER_OUT', 'FEE')
    ),
    CONSTRAINT transaction_sinal_coerente CHECK (
        (type IN ('ADVANCE_CREDIT', 'SETTLEMENT_CREDIT', 'TRANSFER_IN') AND amount > 0)
        OR (type IN ('TRANSFER_OUT', 'FEE') AND amount < 0)
    ),
    CONSTRAINT transaction_origem_unica CHECK (
        NOT (receivable_id IS NOT NULL AND transfer_id IS NOT NULL)
    )
);

CREATE INDEX transaction_extrato_idx ON transaction (account_id, created_at DESC, id DESC);

-- =========================================================
-- dados iniciais dos enumeradores
-- =========================================================
INSERT INTO account_status (enumerator) VALUES ('ACTIVE'), ('BLOCKED'), ('CLOSED');

INSERT INTO receivable_status (enumerator) VALUES
    ('PENDING'), ('ADVANCED'), ('SETTLED'), ('LATE'), ('DEFAULTED');
