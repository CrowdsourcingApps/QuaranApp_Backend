import uuid

from sqlalchemy import Column, ForeignKey, String, Index, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.dal.database import Base
from src.dal.enums import MistakeType


class RecordingMistake(Base):
    __tablename__ = 'recording_mistakes'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    commentator_id = Column(String, ForeignKey('users.id'), nullable=False)
    recording_id = Column(UUID(as_uuid=True), ForeignKey('recordings.id'), nullable=False)
    start_marker_id = Column(UUID(as_uuid=True), ForeignKey('ayah_part_markers.id'), nullable=False)
    end_marker_id = Column(UUID(as_uuid=True), ForeignKey('ayah_part_markers.id'), nullable=False)
    mistake_type = Column(Enum(MistakeType), nullable=False)

    commentator = relationship("User")
    recording = relationship("Recording")

    __table_args__ = (
        Index('ix_recording_mistakes_commentator_id', 'commentator_id'),
        Index('ix_recording_mistakes_recording_id', 'recording_id'),
    )
