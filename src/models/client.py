from sqlalchemy import CHAR, TIMESTAMP, Column, Integer, Text, func

from src.models.base import Base


class Client(Base):
    __tablename__ = "client"

    id = Column(Integer, primary_key=True)
    client_key = Column(CHAR(36), nullable=False, unique=True)
    legal_name = Column(Text, nullable=False)
    document_number = Column(CHAR(14), nullable=False, unique=True)
    email = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
