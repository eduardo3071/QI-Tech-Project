from src.errors.base_error import ApplicationError


class PayerNotFound(ApplicationError):
    status_code = 404
    code = "QIT004001"
    title = "Payer Not Found"
    translation = "Operadora nao encontrada"

    def __init__(self, payer_key: str):
        super().__init__(f"payer_key={payer_key} nao existe")


class PayerAlreadyExists(ApplicationError):
    status_code = 409
    code = "QIT004002"
    title = "Payer Already Exists"
    translation = "Operadora ja cadastrada"

    def __init__(self, document_number: str):
        super().__init__(f"document_number={document_number} ja cadastrado")
