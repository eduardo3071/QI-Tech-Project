from src.errors.base_error import ApplicationError


class AccountNotFound(ApplicationError):
    status_code = 404
    code = "QIT002001"
    title = "Account Not Found"
    translation = "Conta nao encontrada"

    def __init__(self, account_key: str):
        super().__init__(f"account_key={account_key} nao existe")
