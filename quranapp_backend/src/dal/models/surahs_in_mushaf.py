from sqlalchemy import Column, ForeignKey, Integer, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.dal.database import Base


class SurahInMushaf(Base):
    __tablename__ = "surahs_in_mushaf"
    first_page_id = Column(UUID(as_uuid=True), ForeignKey("mushaf_pages.id"), nullable=False)
    surah_number = Column(Integer, ForeignKey("surahs.id"), nullable=False)

    mushaf_page = relationship("MushafPage", back_populates="surahs_in_mushaf")
    surah = relationship("Surah", back_populates="surahs_in_mushaf")

    __table_args__ = (
        PrimaryKeyConstraint('first_page_id', 'surah_number'),
    )
