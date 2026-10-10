from sqlalchemy import BIGINT, CHAR, TIMESTAMP, CheckConstraint, Column, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from src.models.base import Base

CREDIT_TYPES = ("ADVANCE_CREDIT", "SETTLEMENT_CREDIT", "TRANSFER_IN")
DEBIT_TYPES = ("TRANSFER_OUT", "FEE")


class Transaction(Base):
    __tablename__ = "transaction"

    id = Column(Integer, primary_key=True)
    transaction_key = Column(CHAR(36), nullable=False, unique=True)
    account_id = Column(Integer, ForeignKey("account.id"), nullable=False)
    receivable_id = Column(Integer, ForeignKey("receivable.id"), nullable=True)   # antecipacao e liquidacao
    transfer_id = Column(Integer, ForeignKey("transfer.id"), nullable=True)       # transferencia
    type = Column(String(20), nullable=False)
    amount = Column(BIGINT, nullable=False)                        # centavos; negativo em debito
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    account = relationship("Account", foreign_keys=[account_id], lazy="selectin")
    receivable = relationship("Receivable", foreign_keys=[receivable_id], lazy="selectin")
    transfer = relationship("Transfer", foreign_keys=[transfer_id], lazy="selectin")

    __table_args__ = (
        CheckConstraint(
            "type IN ('ADVANCE_CREDIT', 'SETTLEMENT_CREDIT', 'TRANSFER_IN', 'TRANSFER_OUT', 'FEE')",
            name="transaction_type_valido",
        ),
        CheckConstraint(
            "(type IN ('ADVANCE_CREDIT', 'SETTLEMENT_CREDIT', 'TRANSFER_IN') AND amount > 0) "
            "OR (type IN ('TRANSFER_OUT', 'FEE') AND amount < 0)",
            name="transaction_sinal_coerente",
        ),
        CheckConstraint(
            "NOT (receivable_id IS NOT NULL AND transfer_id IS NOT NULL)",
            name="transaction_origem_unica",
        ),
    )
