from datetime import date

from pydantic import BaseModel, conint, constr


class ReceivableCreateSchema(BaseModel):
    payer_key: constr(min_length=36, max_length=36)
    gross_amount: conint(gt=0)    # centavos
    due_date: date
