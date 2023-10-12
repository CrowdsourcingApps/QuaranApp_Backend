import uuid

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID

from src.DAL.database import Base


class AyahPart(Base):
    __tablename__ = "ayah_parts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)