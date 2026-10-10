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


class DuplicatedReceivable(ApplicationError):
    status_code = 409
    code = "QIT003003"
    title = "Duplicated Receivable"
    translation = "Recebivel ja registrado para esta operadora"

    def __init__(self, external_id: str):
        super().__init__(f"external_id={external_id} ja registrado para esta operadora")


class ReceivableOverdue(ApplicationError):
    status_code = 422
    code = "QIT003004"
    title = "Receivable Overdue"
    translation = "Recebivel vencido nao pode ser antecipado"

    def __init__(self, receivable_key: str, due_date: str):
        super().__init__(f"receivable_key={receivable_key} venceu em {due_date}")
