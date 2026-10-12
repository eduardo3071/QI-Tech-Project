from src.errors.base_error import ApplicationError


class ForbiddenNotInternal(ApplicationError):
    status_code = 403
    code = "QIT000403"
    title = "Forbidden"
    translation = "Cabecalho INTERNAL-TOKEN ausente ou invalido"

    def __init__(self):
        super().__init__("a API e interna: envie o cabecalho INTERNAL-TOKEN")


class ForbiddenNotAdmin(ApplicationError):
    status_code = 403
    code = "QIT004005"
    title = "Forbidden Not Admin"
    translation = "Operacao exclusiva do back-office"

    def __init__(self):
        super().__init__("cadastrar operadora exige o cabecalho ADMIN-TOKEN")
