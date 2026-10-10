from sqlalchemy import BIGINT, CHAR, TIMESTAMP, CheckConstraint, Column, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import relationship

from src.models.base import Base


class Transfer(Base):
    __tablename__ = "transfer"

    id = Column(Integer, primary_key=True)
    transfer_key = Column(CHAR(36), nullable=False, unique=True)
    origin_account_id = Column(Integer, ForeignKey("account.id"), nullable=False)
    destination_account_id = Column(Integer, ForeignKey("account.id"), nullable=False)
    amount = Column(BIGINT, nullable=False)                        # centavos, o que chega no destino
    fee_amount = Column(BIGINT, nullable=False)                    # centavos, cobrado da origem
    idempotency_key = Column(CHAR(36), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    origin_account = relationship("Account", foreign_keys=[origin_account_id], lazy="selectin")
    destination_account = relationship("Account", foreign_keys=[destination_account_id], lazy="selectin")

    __table_args__ = (
        UniqueConstraint("origin_account_id", "idempotency_key", name="transfer_idempotente"),
        CheckConstraint("origin_account_id <> destination_account_id", name="transfer_contas_distintas"),
        CheckConstraint("amount > 0", name="transfer_amount_positivo"),
        CheckConstraint("fee_amount >= 0", name="transfer_fee_nao_negativa"),
    )
