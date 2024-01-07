import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.dal.database import Base


class Recording(Base):
    __tablename__ = "recordings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # todo проверить, нужен ли тут as_uuid=True
    # todo подумать про ON_DELETE опцию
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    start_id = Column(UUID(as_uuid=True), ForeignKey("ayah_parts.id"), nullable=False)
    end_id = Column(UUID(as_uuid=True), ForeignKey("ayah_parts.id"), nullable=False)
    audio_url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    user = relationship("User", back_populates="recordings")
    start = relationship("AyahPart", foreign_keys=[start_id])
    end = relationship("AyahPart", foreign_keys=[end_id])
