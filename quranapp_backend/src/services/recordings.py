from sqlalchemy.orm import Session

from src.dal.models import Recording, AyahPart, User


def create_recording(db: Session, user: User, start: AyahPart, end: AyahPart, audio_url: str):
    db_recording = Recording(user=user, start=start, end=end, audio_url=audio_url)
    db.add(db_recording)
    db.commit()
    db.refresh(db_recording)
    return db_recording
