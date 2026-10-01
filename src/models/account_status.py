from sqlalchemy import Column, Integer, String

from src.models.base import Base


class AccountStatus(Base):
    __tablename__ = "account_status"

    id = Column(Integer, primary_key=True)
    enumerator = Column(String(20), nullable=False, unique=True)
