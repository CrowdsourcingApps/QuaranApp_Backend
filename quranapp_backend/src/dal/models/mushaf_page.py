import uuid

from sqlalchemy import Column, String, SmallInteger, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.dal.database import Base


class MushafPage(Base):
    __tablename__ = "mushaf_pages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    index = Column(SmallInteger, nullable=False)
    mushaf_id = Column(UUID(as_uuid=True), ForeignKey("mushafs.id"), nullable=False)
    light_mode_link = Column(String, nullable=True)
    dark_mode_link = Column(String, nullable=True)

    mushaf = relationship("Mushaf", back_populates="pages")
    ayah_parts = relationship("AyahPart", back_populates="mushaf_page")
    surahs_in_mushaf = relationship("SurahInMushaf", back_populates="mushaf_page")
