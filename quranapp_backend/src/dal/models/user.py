import uuid

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from src.dal.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    alias = Column(String, default=f'user{uuid.uuid4().hex}', unique=True, nullable=False)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    recordings = relationship("Recording", back_populates="user")
    tokens = relationship("Token", back_populates="user")
