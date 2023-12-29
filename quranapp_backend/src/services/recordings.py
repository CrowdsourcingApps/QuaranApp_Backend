import uuid

from sqlalchemy.orm import Session

from src.dal.models import Recording, AyahPart, SharedRecording

from src.models import RecordingShare


def create_recording(db: Session, user_id: str, start: AyahPart, end: AyahPart, audio_url: str) -> Recording:
    db_recording = Recording(user_id=user_id, start=start, end=end, audio_url=audio_url)
    db.add(db_recording)
    db.commit()
    db.refresh(db_recording)
    return db_recording


def get_my_recordings(db: Session, user_id: str) -> list[Recording]:
    return db.query(Recording).filter(Recording.user_id == user_id).all()


def share_recording(db: Session, share_data: RecordingShare) -> SharedRecording:
    db_shared_recoding = SharedRecording(recipient_id=share_data.recipient_id, recording_id=share_data.recording_id)
    db.add(db_shared_recoding)
    db.commit()
    db.refresh(db_shared_recoding)
    return db_shared_recoding


def is_recording_exist(db: Session, recording_id: uuid.UUID):
    result = db.query(Recording.id).filter_by(id=recording_id).first() is not None
    return result
