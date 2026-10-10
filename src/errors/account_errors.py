from src.errors.base_error import ApplicationError


class AccountNotFound(ApplicationError):
    status_code = 404
    code = "QIT002001"
    title = "Account Not Found"
    translation = "Conta nao encontrada"

    def __init__(self, account_key: str):
        super().__init__(f"account_key={account_key} nao existe")


class AccountNotActive(ApplicationError):
    status_code = 409
    code = "QIT002002"
    title = "Account Not Active"
    translation = "Conta nao esta ativa"

    def __init__(self, account_key: str, current_status: str):
        super().__init__(f"account_key={account_key} esta em {current_status}, a operacao exige ACTIVE")


class InsufficientBalance(ApplicationError):
    status_code = 422
    code = "QIT002003"
    title = "Insufficient Balance"
    translation = "Saldo insuficiente"

    def __init__(self, account_key: str, balance: int, required: int):
        super().__init__(f"account_key={account_key} tem {balance} centavos, a operacao exige {required}")


class InvalidAccountStatusTransition(ApplicationError):
    status_code = 409
    code = "QIT002004"
    title = "Invalid Account Status Transition"
    translation = "Mudanca de estado da conta nao permitida"

    def __init__(self, account_key: str, from_status: str, to_status: str):
        super().__init__(f"account_key={account_key} nao pode ir de {from_status} para {to_status}")


class AccountCannotBeClosed(ApplicationError):
    status_code = 409
    code = "QIT002005"
    title = "Account Cannot Be Closed"
    translation = "Conta nao pode ser encerrada"

    def __init__(self, account_key: str, motive: str):
        super().__init__(f"account_key={account_key} nao pode ser encerrada: {motive}")


class ReferencedAccountNotFound(ApplicationError):
    # a conta veio no corpo, nao no caminho: o pedido esta bem formado mas aponta
    # para algo que nao existe -> 422, nao 404
    status_code = 422
    code = "QIT002006"
    title = "Referenced Account Not Found"
    translation = "Conta informada no corpo nao existe"

    def __init__(self, account_key: str):
        super().__init__(f"destination_account_key={account_key} nao existe")
