from pydantic import BaseModel, constr


class PayerCreateSchema(BaseModel):
    legal_name: constr(min_length=1, max_length=255)
    document_number: constr(min_length=14, max_length=14)
