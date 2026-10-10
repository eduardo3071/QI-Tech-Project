from src.errors.base_error import ApplicationError


class PayerAlreadyExists(ApplicationError):
    status_code = 409
    code = "QIT004002"
    title = "Payer Already Exists"
    translation = "Operadora ja cadastrada"

    def __init__(self, document_number: str):
        super().__init__(f"document_number={document_number} ja cadastrado")


class ReferencedPayerNotFound(ApplicationError):
    # payer_key vem no corpo do recebivel: referencia invalida -> 422
    status_code = 422
    code = "QIT004003"
    title = "Referenced Payer Not Found"
    translation = "Operadora informada no corpo nao existe"

    def __init__(self, payer_key: str):
        super().__init__(f"payer_key={payer_key} nao existe")
