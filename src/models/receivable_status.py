from sqlalchemy import Column, Integer, String

from src.models.base import Base


class ReceivableStatus(Base):
    __tablename__ = "receivable_status"

    id = Column(Integer, primary_key=True)
    enumerator = Column(String(20), nullable=False, unique=True)
