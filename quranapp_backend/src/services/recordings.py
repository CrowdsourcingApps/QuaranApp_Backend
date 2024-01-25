import uuid

from sqlalchemy.orm import Session

from src.dal.models import Recording, AyahPart, SharedRecording
from src.models import DetailedRecording, AyahPartDetailed


def create_recording(db: Session, user_id: str, start: AyahPart, end: AyahPart, audio_url: str) -> Recording:
    db_recording = Recording(user_id=user_id, start=start, end=end, audio_url=audio_url)
    db.add(db_recording)
    db.commit()
    db.refresh(db_recording)
    return db_recording


def get_my_recordings(db: Session, user_id: str) -> list[DetailedRecording]:
    recordings = db.query(Recording).filter_by(user_id=user_id).all()
    result = []
    for recording in recordings:
        start = recording.start
        end = recording.end

        result.append(DetailedRecording(
            id=recording.id,
            user_alias=recording.user.alias,
            riwayah=start.ayah.riwayah,
            start=AyahPartDetailed(
                surah_number=start.ayah.surah_number,
                ayah_in_surah_number=start.ayah.ayah_in_surah_number,
                part_number=start.part_number),
            end=AyahPartDetailed(
                surah_number=end.ayah.surah_number,
                ayah_in_surah_number=end.ayah.ayah_in_surah_number,
                part_number=end.part_number),
            created_at=recording.created_at,
            audio_url=recording.audio_url))

    return result


def get_shared_with_me_recordings(db: Session, user_id: str) -> list[DetailedRecording]:
    shared_recordings = db.query(SharedRecording).filter_by(recipient_id=user_id).all()
    result = []
    for shared in shared_recordings:
        start = shared.recording.start
        end = shared.recording.end

        result.append(DetailedRecording(
            id=shared.recording.id,
            user_alias=shared.recording.user.alias,
            riwayah=start.ayah.riwayah,
            start=AyahPartDetailed(
                surah_number=start.ayah.surah_number,
                ayah_in_surah_number=start.ayah.ayah_in_surah_number,
                part_number=start.part_number),
            end=AyahPartDetailed(
                surah_number=end.ayah.surah_number,
                ayah_in_surah_number=end.ayah.ayah_in_surah_number,
                part_number=end.part_number),
            created_at=shared.recording.created_at,
            audio_url=shared.recording.audio_url))

    return result


def get_available_recordings(db: Session, user_id: str) -> list[DetailedRecording]:
    my_recordings = get_my_recordings(db, user_id)
    shared_recordings = get_shared_with_me_recordings(db, user_id)

    return my_recordings + shared_recordings


def share_recording(db: Session, recording_id: uuid.UUID, recipient_id: str) -> SharedRecording:
    db_shared_recoding = SharedRecording(recipient_id=recipient_id, recording_id=recording_id)
    db.add(db_shared_recoding)
    db.commit()
    db.refresh(db_shared_recoding)
    return db_shared_recoding


def get_recording_by_id(db: Session, recording_id: uuid.UUID):
    return db.query(Recording).filter_by(id=recording_id).first()
