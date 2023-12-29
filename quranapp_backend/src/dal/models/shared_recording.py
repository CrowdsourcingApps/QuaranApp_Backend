import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, PrimaryKeyConstraint, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.dal.database import Base


class SharedRecording(Base):
    __tablename__ = 'shared_recordings'
    recipient_id = Column(String, ForeignKey('users.id'), nullable=False)
    recording_id = Column(UUID(as_uuid=True), ForeignKey('recordings.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    recipient = relationship("User")
    recording = relationship("Recording")

    __table_args__ = (
        PrimaryKeyConstraint('recipient_id', 'recording_id'),
    )
