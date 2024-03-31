import uuid

from sqlalchemy import Column, Enum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.dal.database import Base
from src.dal.enums import RiwayahEnum, PublisherEnum


class Mushaf(Base):
    __tablename__ = "mushafs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    publisher = Column(Enum(PublisherEnum), nullable=False)
    riwayah = Column(Enum(RiwayahEnum), nullable=False)

    ayahs = relationship("Ayah", back_populates="mushaf")
    pages = relationship("MushafPage", back_populates="mushaf")

    __table_args__ = (
        Index('ix_mushafs_publisher_riwayah', 'publisher', 'riwayah', unique=True),
    )
