from sqlalchemy.orm import Session

from src.dal.models import Recording, AyahPart


def create_recording(db: Session, user_id: str, start: AyahPart, end: AyahPart, audio_url: str):
    db_recording = Recording(user_id=user_id, start=start, end=end, audio_url=audio_url)
    db.add(db_recording)
    db.commit()
    db.refresh(db_recording)
    return db_recording
