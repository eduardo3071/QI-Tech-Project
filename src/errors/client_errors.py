from src.errors.base_error import ApplicationError


class ClientNotFound(ApplicationError):
    status_code = 404
    code = "QIT001001"
    title = "Client Not Found"
    translation = "Cliente nao encontrado"

    def __init__(self, client_key: str):
        super().__init__(f"client_key={client_key} nao existe")


class ClientAlreadyExists(ApplicationError):
    status_code = 409
    code = "QIT001002"
    title = "Client Already Exists"
    translation = "Cliente ja cadastrado"

    def __init__(self, document_number: str):
        super().__init__(f"document_number={document_number} ja cadastrado")
