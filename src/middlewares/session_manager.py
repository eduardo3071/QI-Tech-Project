from fastapi import FastAPI, Request

from src.database import SessionLocal


def register_session_manager_middleware(application: FastAPI) -> None:
    """Abre a sessao do banco no inicio de cada requisicao e a fecha no fim.

    - rollback se a requisicao terminou em excecao nao tratada;
    - close SEMPRE (fechar sem commit tambem desfaz o rascunho);
    - commit NUNCA: quem sabe que o trabalho terminou e o controller.

    A sessao do SQLAlchemy so pega conexao na primeira consulta, entao rotas
    que nao tocam no banco nao gastam conexao."""

    @application.middleware("http")
    async def manage_session(request: Request, call_next):
        session = SessionLocal()
        request.state.db_session = session
        try:
            return await call_next(request)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
