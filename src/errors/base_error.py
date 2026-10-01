class ApplicationError(Exception):
    status_code: int = 500
    code: str = "QIT000000"
    title: str = "Internal Server Error"
    translation: str = "Erro interno do servidor"

    def __init__(self, description: str):
        self.description = description
        super().__init__(description)

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "description": self.description,
            "translation": self.translation,
            "code": self.code,
        }
