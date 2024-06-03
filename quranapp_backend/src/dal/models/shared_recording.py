from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, PrimaryKeyConstraint, String, Index, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.dal.database import Base


class SharedRecording(Base):
    __tablename__ = 'shared_recordings'
    recipient_id = Column(String, ForeignKey('users.id'), nullable=False)
    recording_id = Column(UUID(as_uuid=True), ForeignKey('recordings.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    is_reviewed = Column(Boolean, default=False, nullable=True)

    recipient = relationship("User")
    recording = relationship("Recording", back_populates="shares")

    __table_args__ = (
        PrimaryKeyConstraint('recipient_id', 'recording_id'),
        Index('ix_shared_recordings_recipient_id', 'recipient_id'),
        Index('ix_shared_recordings_recording_id', 'recording_id'),
    )
