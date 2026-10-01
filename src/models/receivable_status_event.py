from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from src.models.base import Base


class ReceivableStatusEvent(Base):
    __tablename__ = "receivable_status_event"

    id = Column(Integer, primary_key=True)
    receivable_id = Column(Integer, ForeignKey("receivable.id"), nullable=False)
    from_status_id = Column(Integer, ForeignKey("receivable_status.id"), nullable=True)   # nulo ao nascer
    to_status_id = Column(Integer, ForeignKey("receivable_status.id"), nullable=False)
    reason = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    receivable = relationship("Receivable", foreign_keys=[receivable_id], lazy="selectin")
    from_status = relationship("ReceivableStatus", foreign_keys=[from_status_id], lazy="selectin")
    to_status = relationship("ReceivableStatus", foreign_keys=[to_status_id], lazy="selectin")
