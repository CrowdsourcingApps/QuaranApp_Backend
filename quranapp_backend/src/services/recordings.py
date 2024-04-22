import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.dal.models import Recording, AyahPart, SharedRecording
from src.models import DetailedRecording, AyahPartDetailed


def create_recording(
        db: Session, recording_id: uuid.UUID, user_id: str, start: AyahPart, end: AyahPart, audio_url: str
) -> Recording:
    db_recording = Recording(id=recording_id, user_id=user_id, start=start, end=end, audio_url=audio_url)
    db.add(db_recording)
    db.commit()
    db.refresh(db_recording)
    return db_recording


def get_range_string(start: AyahPart, end: AyahPart):
    start_surah_name = start.ayah.surah.title_eng
    if start.ayah.surah_number == end.ayah.surah_number:
        range_string = f'{start_surah_name} {start.ayah.ayah_in_surah_number}-{end.ayah.ayah_in_surah_number}'
    else:
        end_surah_name = start.ayah.surah.title_eng
        range_string = f'{start_surah_name} {start.ayah.ayah_in_surah_number} - {end_surah_name} {end.ayah.ayah_in_surah_number}'

    return range_string


def get_my_recordings(db: Session, user_id: str) -> list[DetailedRecording]:
    recordings = (db.query(Recording)
                  .filter_by(user_id=user_id)
                  .filter(Recording.is_deleted.isnot(True))
                  .all())
    result = []
    for recording in recordings:
        start = recording.start
        end = recording.end
        range_string = get_range_string(start, end)

        result.append(DetailedRecording(
            id=recording.id,
            user_alias=recording.user.alias,
            is_my_recording=True,
            riwayah=start.ayah.mushaf.riwayah,
            publisher=start.ayah.mushaf.publisher,
            start=AyahPartDetailed(
                surah_number=start.ayah.surah_number,
                ayah_in_surah_number=start.ayah.ayah_in_surah_number,
                part_number=start.part_number),
            end=AyahPartDetailed(
                surah_number=end.ayah.surah_number,
                ayah_in_surah_number=end.ayah.ayah_in_surah_number,
                part_number=end.part_number),
            range_string=range_string,
            created_at=recording.created_at,
            audio_url=recording.audio_url))

    return result


def get_shared_with_me_recordings(db: Session, user_id: str) -> list[DetailedRecording]:
    shared_recordings = db.query(SharedRecording).filter(
        SharedRecording.recording.has(Recording.is_deleted.isnot(True)),
        SharedRecording.recipient_id == user_id,
    ).all()

    result = []
    for shared in shared_recordings:
        start = shared.recording.start
        end = shared.recording.end
        range_string = get_range_string(start, end)

        result.append(DetailedRecording(
            id=shared.recording.id,
            user_alias=shared.recording.user.alias,
            is_my_recording=False,
            riwayah=start.ayah.mushaf.riwayah,
            publisher=start.ayah.mushaf.publisher,
            start=AyahPartDetailed(
                surah_number=start.ayah.surah_number,
                ayah_in_surah_number=start.ayah.ayah_in_surah_number,
                part_number=start.part_number),
            end=AyahPartDetailed(
                surah_number=end.ayah.surah_number,
                ayah_in_surah_number=end.ayah.ayah_in_surah_number,
                part_number=end.part_number),
            range_string=range_string,
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


def get_recording_by_id(db: Session, recording_id: uuid.UUID) -> Recording:
    recording = db.get(Recording, recording_id)
    if recording is None or recording.is_deleted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Recording with given id does not exist')
    return recording  # noqa


def check_if_recording_exists(db: Session, recording_id: uuid.UUID) -> bool:
    return bool(db.get(Recording, recording_id))


def delete_recording(db: Session, recording_id: uuid.UUID) -> None:
    recording = get_recording_by_id(db, recording_id)
    recording.is_deleted = True
    db.commit()


def check_recording_owner(db: Session, user_id: str, recording_id: uuid.UUID) -> bool:
    recording = get_recording_by_id(db, recording_id)
    if user_id != recording.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return True
