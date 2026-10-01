from sqlalchemy import BIGINT, CHAR, TIMESTAMP, CheckConstraint, Column, ForeignKey, Integer, func
from sqlalchemy.orm import relationship

from src.models.base import Base


class Account(Base):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True)                        # interno: as relacoes usam este
    account_key = Column(CHAR(36), nullable=False, unique=True)    # externo: e o que sai na URL
    client_id = Column(Integer, ForeignKey("client.id"), nullable=False)
    status_id = Column(Integer, ForeignKey("account_status.id"), nullable=False)
    balance = Column(BIGINT, nullable=False, default=0)            # centavos, inteiro
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    client = relationship("Client", foreign_keys=[client_id], lazy="selectin")
    status = relationship("AccountStatus", foreign_keys=[status_id], lazy="selectin")

    __table_args__ = (CheckConstraint("balance >= 0", name="balance_nao_negativo"),)
