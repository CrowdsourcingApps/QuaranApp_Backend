from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from src.dal.database import Base


class Token(Base):
    __tablename__ = 'tokens'
    user_id = Column(String, ForeignKey("users.id"), primary_key=True, nullable=False)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)

    user = relationship("User", back_populates="tokens")
