-- QI Tech Bootcamp 2026 · Antecipa Saude
-- Fase 0 - Banco de dados (PostgreSQL)
-- Roda uma vez, quando o banco nasce.

-- =========================================================
-- client: a clinica ou hospital que cadastra recebiveis
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
-- account: a conta da clinica, onde entra o dinheiro antecipado
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
-- payer: a operadora/convenio devedora do recebivel
-- =========================================================
CREATE TABLE payer (
    id              SERIAL PRIMARY KEY,
    payer_key       CHAR(36) NOT NULL UNIQUE,
    legal_name      TEXT     NOT NULL,
    document_number CHAR(14) NOT NULL UNIQUE,
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
-- receivable: o valor que a clinica tem a receber da operadora
-- =========================================================
CREATE TABLE receivable (
    id           SERIAL PRIMARY KEY,
    receivable_key CHAR(36)  NOT NULL UNIQUE,
    account_id   INTEGER    NOT NULL REFERENCES account(id),
    payer_id     INTEGER    NOT NULL REFERENCES payer(id),
    gross_amount BIGINT     NOT NULL,                           -- centavos, o valor cheio do convenio
    due_date     DATE       NOT NULL,
    status_id    INTEGER    NOT NULL REFERENCES receivable_status(id),
    created_at   TIMESTAMP  NOT NULL DEFAULT now(),
    updated_at   TIMESTAMP  NOT NULL DEFAULT now(),
    CONSTRAINT gross_amount_positivo CHECK (gross_amount > 0)
);

-- =========================================================
-- receivable_status_event: uma linha por mudanca de estado
-- exigencia regulatoria em sistema financeiro: guarda o caminho,
-- nao so o estado atual.
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
-- advance: a operacao de antecipacao em si - um recebivel so
-- pode ser antecipado uma vez (UNIQUE em receivable_id)
-- =========================================================
CREATE TABLE advance (
    id           SERIAL PRIMARY KEY,
    advance_key  CHAR(36)  NOT NULL UNIQUE,
    receivable_id INTEGER  NOT NULL REFERENCES receivable(id),
    fee_rate     NUMERIC(5,4) NOT NULL,                         -- ex.: 0.0350 = 3,5%
    fee_amount   BIGINT    NOT NULL,                             -- centavos
    net_amount   BIGINT    NOT NULL,                             -- centavos, o que cai na conta
    advanced_at  TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT advance_unico_por_recebivel UNIQUE (receivable_id),
    CONSTRAINT fee_amount_nao_negativo CHECK (fee_amount >= 0),
    CONSTRAINT net_amount_positivo CHECK (net_amount > 0)
);

-- =========================================================
-- transaction: toda movimentacao de conta - credito da
-- antecipacao, debito da tarifa, debito no settlement
-- =========================================================
CREATE TABLE transaction (
    id             SERIAL PRIMARY KEY,
    transaction_key CHAR(36) NOT NULL UNIQUE,
    account_id     INTEGER  NOT NULL REFERENCES account(id),
    receivable_id  INTEGER  REFERENCES receivable(id),          -- nulo em movimentacoes sem recebivel associado
    type           VARCHAR(20) NOT NULL,                        -- ADVANCE_CREDIT | FEE | SETTLEMENT_CREDIT
    amount         BIGINT   NOT NULL,                            -- centavos; negativo em debito, positivo em credito
    created_at     TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT transaction_type_valido CHECK (type IN ('ADVANCE_CREDIT', 'FEE', 'SETTLEMENT_CREDIT'))
);

-- =========================================================
-- dados iniciais dos enumeradores
-- =========================================================
INSERT INTO account_status (enumerator) VALUES ('ACTIVE'), ('BLOCKED'), ('CLOSED');

INSERT INTO receivable_status (enumerator) VALUES
    ('PENDING'), ('ADVANCED'), ('SETTLED'), ('LATE'), ('DEFAULTED');
