import uuid

from sqlalchemy import Column, SmallInteger
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from src.dal.database import Base


class Ayah(Base):
    __tablename__ = "ayahs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    surah_number = Column(SmallInteger, nullable=False)
    ayah_in_surah_number = Column(SmallInteger, nullable=False)
    # riwayah

    ayah_parts = relationship("AyahPart", back_populates="ayah")
