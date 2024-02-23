import uuid

from sqlalchemy import Column, SmallInteger, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.dal.database import Base


class AyahPart(Base):
    __tablename__ = "ayah_parts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ayah_id = Column(UUID(as_uuid=True), ForeignKey("ayahs.id"), nullable=False)
    mushaf_page_id = Column(UUID(as_uuid=True), ForeignKey("mushaf_pages.id"), nullable=True)
    part_number = Column(SmallInteger, nullable=False)
    ayah_part_text_id = Column(UUID(as_uuid=True), ForeignKey("ayah_part_texts.id"), nullable=True)

    ayah = relationship("Ayah", back_populates="ayah_parts")
    mushaf_page = relationship("MushafPage", back_populates="ayah_parts")
    markers = relationship("AyahPartMarker", back_populates="ayah_part")
    text = relationship("AyahPartText", back_populates="ayah_parts")
