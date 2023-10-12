from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from src.DAL.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)

    recordings = relationship("Recording", back_populates="user")