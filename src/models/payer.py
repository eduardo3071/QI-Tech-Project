from sqlalchemy import CHAR, TIMESTAMP, Column, Integer, Text, func

from src.models.base import Base


class Payer(Base):
    __tablename__ = "payer"

    id = Column(Integer, primary_key=True)
    payer_key = Column(CHAR(36), nullable=False, unique=True)
    legal_name = Column(Text, nullable=False)
    document_number = Column(CHAR(14), nullable=False, unique=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
