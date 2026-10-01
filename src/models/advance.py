from sqlalchemy import BIGINT, CHAR, TIMESTAMP, CheckConstraint, Column, ForeignKey, Integer, Numeric, func
from sqlalchemy.orm import relationship

from src.models.base import Base


class Advance(Base):
    __tablename__ = "advance"

    id = Column(Integer, primary_key=True)
    advance_key = Column(CHAR(36), nullable=False, unique=True)
    receivable_id = Column(Integer, ForeignKey("receivable.id"), nullable=False, unique=True)  # um por recebivel
    fee_rate = Column(Numeric(5, 4), nullable=False)               # ex.: 0.0350 = 3,5%
    fee_amount = Column(BIGINT, nullable=False)                    # centavos
    net_amount = Column(BIGINT, nullable=False)                    # centavos, o que cai na conta
    advanced_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    receivable = relationship("Receivable", foreign_keys=[receivable_id], lazy="selectin")

    __table_args__ = (
        CheckConstraint("fee_amount >= 0", name="fee_amount_nao_negativo"),
        CheckConstraint("net_amount > 0", name="net_amount_positivo"),
    )
