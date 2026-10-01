from sqlalchemy import BIGINT, CHAR, TIMESTAMP, CheckConstraint, Column, Date, ForeignKey, Integer, func
from sqlalchemy.orm import relationship

from src.models.base import Base


class Receivable(Base):
    __tablename__ = "receivable"

    id = Column(Integer, primary_key=True)
    receivable_key = Column(CHAR(36), nullable=False, unique=True)
    account_id = Column(Integer, ForeignKey("account.id"), nullable=False)
    payer_id = Column(Integer, ForeignKey("payer.id"), nullable=False)
    gross_amount = Column(BIGINT, nullable=False)                  # centavos, o valor cheio do convenio
    due_date = Column(Date, nullable=False)
    status_id = Column(Integer, ForeignKey("receivable_status.id"), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    account = relationship("Account", foreign_keys=[account_id], lazy="selectin")
    payer = relationship("Payer", foreign_keys=[payer_id], lazy="selectin")
    status = relationship("ReceivableStatus", foreign_keys=[status_id], lazy="selectin")

    __table_args__ = (CheckConstraint("gross_amount > 0", name="gross_amount_positivo"),)
