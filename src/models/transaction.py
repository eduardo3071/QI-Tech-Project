from sqlalchemy import BIGINT, CHAR, TIMESTAMP, CheckConstraint, Column, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from src.models.base import Base


class Transaction(Base):
    __tablename__ = "transaction"

    id = Column(Integer, primary_key=True)
    transaction_key = Column(CHAR(36), nullable=False, unique=True)
    account_id = Column(Integer, ForeignKey("account.id"), nullable=False)
    receivable_id = Column(Integer, ForeignKey("receivable.id"), nullable=True)   # nulo quando nao associado
    type = Column(String(20), nullable=False)                      # ADVANCE_CREDIT | FEE | SETTLEMENT_CREDIT
    amount = Column(BIGINT, nullable=False)                        # centavos; negativo em debito, positivo em credito
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    account = relationship("Account", foreign_keys=[account_id], lazy="selectin")
    receivable = relationship("Receivable", foreign_keys=[receivable_id], lazy="selectin")

    __table_args__ = (
        CheckConstraint(
            "type IN ('ADVANCE_CREDIT', 'FEE', 'SETTLEMENT_CREDIT')",
            name="transaction_type_valido",
        ),
    )
