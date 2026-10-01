from src.errors.base_error import ApplicationError


class ReceivableNotFound(ApplicationError):
    status_code = 404
    code = "QIT003001"
    title = "Receivable Not Found"
    translation = "Recebivel nao encontrado"

    def __init__(self, receivable_key: str):
        super().__init__(f"receivable_key={receivable_key} nao existe")


class ReceivableNotAdvanceable(ApplicationError):
    status_code = 409
    code = "QIT003002"
    title = "Receivable Not Advanceable"
    translation = "Recebivel nao pode ser antecipado neste estado"

    def __init__(self, receivable_key: str, current_status: str):
        super().__init__(f"receivable_key={receivable_key} esta em {current_status}, nao em PENDING")
