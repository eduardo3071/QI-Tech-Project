from pydantic import BaseModel, ConfigDict, constr


class PayerCreateSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    legal_name: constr(strip_whitespace=True, min_length=1, max_length=255)
    document_number: constr(pattern=r"^[0-9A-Z]{14}$")
