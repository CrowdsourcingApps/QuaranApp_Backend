import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.dal.database import Base


class SharedRecording(Base):
    __tablename__ = 'shared_recordings'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipient_id = Column(String, ForeignKey('users.id'), nullable=False)
    recording_id = Column(UUID(as_uuid=True), ForeignKey('recordings.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    recipient = relationship("User")
    recording = relationship("Recording")
