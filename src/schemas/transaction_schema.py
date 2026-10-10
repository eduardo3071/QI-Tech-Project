from typing import Literal

from pydantic import BaseModel, ConfigDict, conint, constr

from src.schemas.receivable_schema import UUID_PATTERN


class TransactionCreateSchema(BaseModel):
    """Movimentacao iniciada pela clinica. Hoje o unico tipo e TRANSFER;
    os demais lancamentos (antecipacao, tarifa, liquidacao) nascem das regras do sistema."""

    model_config = ConfigDict(extra="forbid")

    type: Literal["TRANSFER"]
    destination_account_key: constr(pattern=UUID_PATTERN)
    amount: conint(gt=0, le=10_000_000_000)   # centavos
    idempotency_key: constr(pattern=UUID_PATTERN)  # gerado pelo cliente, um por intencao de pagamento
