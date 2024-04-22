import uuid

from sqlalchemy import Column, SmallInteger, ForeignKey, Integer, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.dal.database import Base


class Ayah(Base):
    __tablename__ = "ayahs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mushaf_id = Column(UUID(as_uuid=True), ForeignKey("mushafs.id"), nullable=False)
    surah_number = Column(Integer, ForeignKey("surahs.id"), nullable=False)
    ayah_in_surah_number = Column(SmallInteger, nullable=False)

    mushaf = relationship("Mushaf", back_populates="ayahs")
    ayah_parts = relationship("AyahPart", back_populates="ayah")
    surah = relationship("Surah", back_populates="ayahs")

    __table_args__ = (
        Index('ix_ayahs_surah_number', 'surah_number'),
        Index('ix_ayahs_ayah_in_surah_number', 'ayah_in_surah_number'),
    )
