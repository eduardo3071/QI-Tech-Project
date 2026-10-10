from datetime import date

from pydantic import BaseModel, ConfigDict, conint, constr

UUID_PATTERN = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"


class ReceivableCreateSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    payer_key: constr(pattern=UUID_PATTERN)
    external_id: constr(strip_whitespace=True, min_length=1, max_length=64)  # numero da guia/fatura
    gross_amount: conint(gt=0, le=10_000_000_000)                           # centavos
    due_date: date
