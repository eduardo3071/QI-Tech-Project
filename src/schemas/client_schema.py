from pydantic import BaseModel, ConfigDict, EmailStr, constr


class ClientCreateSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")  # o que nao esta no contrato nao entra

    legal_name: constr(strip_whitespace=True, min_length=1, max_length=255)
    document_number: constr(pattern=r"^[0-9A-Z]{14}$")  # CNPJ sem mascara
    email: EmailStr
