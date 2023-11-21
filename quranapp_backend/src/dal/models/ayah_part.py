import uuid

from sqlalchemy import Column, SmallInteger, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from src.dal.database import Base


class AyahPart(Base):
    __tablename__ = "ayah_parts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    part_number = Column(SmallInteger, nullable=False)
    ayah_id = Column(UUID(as_uuid=True), ForeignKey("ayahs.id"), nullable=False)

    ayah = relationship("Ayah", back_populates="ayah_parts")
