import uuid

from sqlalchemy import Column, SmallInteger, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.dal.database import Base


class AyahPartMarker(Base):
    __tablename__ = "ayah_part_markers"
    ayah_part_id = Column(UUID(as_uuid=True), ForeignKey("ayah_parts.id"), primary_key=True)
    order = Column(SmallInteger, primary_key=True)
    x = Column(SmallInteger, nullable=False)
    y1 = Column(SmallInteger, nullable=False)
    y2 = Column(SmallInteger, nullable=False)
    is_new_line = Column(Boolean, default=False, nullable=False)

    ayah_part = relationship("AyahPart", back_populates="markers")
