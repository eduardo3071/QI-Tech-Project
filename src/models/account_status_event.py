from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from src.models.base import Base


class AccountStatusEvent(Base):
    __tablename__ = "account_status_event"

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("account.id"), nullable=False)
    from_status_id = Column(Integer, ForeignKey("account_status.id"), nullable=True)   # nulo ao nascer
    to_status_id = Column(Integer, ForeignKey("account_status.id"), nullable=False)
    reason = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    from_status = relationship("AccountStatus", foreign_keys=[from_status_id], lazy="selectin")
    to_status = relationship("AccountStatus", foreign_keys=[to_status_id], lazy="selectin")
