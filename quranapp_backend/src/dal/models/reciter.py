import uuid

from sqlalchemy import Column, String, Enum
from sqlalchemy.dialects.postgresql import UUID

from src.dal.database import Base
from src.dal.enums import RiwayahEnum


class Reciter(Base):
    __tablename__ = "reciters"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    riwayah = Column(Enum(RiwayahEnum), nullable=False)
