from sqlalchemy.orm import Session

from src.dal.models import Recording, AyahPart


def create_recording(db: Session, user_id: str, start: AyahPart, end: AyahPart, audio_url: str):
    db_recording = Recording(user_id=user_id, start=start, end=end, audio_url=audio_url)
    db.add(db_recording)
    db.commit()
    db.refresh(db_recording)
    return db_recording


def get_my_recordings(db: Session, user_id: str) -> list[Recording]:
    return db.query(Recording).filter(Recording.user_id == user_id).all()
