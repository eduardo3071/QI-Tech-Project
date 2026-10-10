from src.errors.base_error import ApplicationError


class SameAccountTransfer(ApplicationError):
    status_code = 422
    code = "QIT005001"
    title = "Same Account Transfer"
    translation = "Origem e destino sao a mesma conta"

    def __init__(self, account_key: str):
        super().__init__(f"account_key={account_key} e origem e destino")


class IdempotencyKeyReused(ApplicationError):
    status_code = 409
    code = "QIT005002"
    title = "Idempotency Key Reused"
    translation = "Chave de idempotencia ja usada com outro pedido"

    def __init__(self, idempotency_key: str):
        super().__init__(f"idempotency_key={idempotency_key} ja foi usada com outro destino ou valor")
