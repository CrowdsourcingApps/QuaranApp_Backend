import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from src.controllers.dependencies import db_session_dependency, transform_recording_data, api_key_dependency, \
    jwt_dependency
from src.models import Recording, RecordingShare, SharedRecording, DetailedRecording
from src.services import azure_blob_storage, recordings as recordings_service, ayah_parts, users_service

recordings_router = APIRouter(
    prefix="/recordings",
    tags=["recordings"],
    dependencies=[api_key_dependency]
)


@recordings_router.get("/my", response_model=list[DetailedRecording])
def get_my_recordings(user_id: str = jwt_dependency, db: Session = db_session_dependency):
    user = users_service.get_user_by_id(db, user_id)  # noqa
    if not user:
        raise HTTPException(detail="User not found by ID", status_code=status.HTTP_400_BAD_REQUEST)
    return recordings_service.get_my_recordings(db, user.id)


@recordings_router.get("/shared_with_me", response_model=list[DetailedRecording])
def get_shared_recordings(user_id: str = jwt_dependency, db: Session = db_session_dependency):
    user = users_service.get_user_by_id(db, user_id)  # noqa
    if not user:
        raise HTTPException(detail="User not found by ID", status_code=status.HTTP_400_BAD_REQUEST)
    return recordings_service.get_shared_with_me_recordings(db, user.id)


@recordings_router.get("/available", response_model=list[DetailedRecording])
def get_available_recordings(user_id: str = jwt_dependency, db: Session = db_session_dependency):
    user = users_service.get_user_by_id(db, user_id)  # noqa
    if not user:
        raise HTTPException(detail="User not found by ID", status_code=status.HTTP_400_BAD_REQUEST)
    return recordings_service.get_available_recordings(db, user.id)


@recordings_router.post("/upload", response_model=Recording)
def upload_recording(
        audio_file: UploadFile,
        recording_data: Annotated[str, Depends(transform_recording_data)],
        db: Session = db_session_dependency
):
    user = users_service.get_user_by_id(db, recording_data.user_id)
    if not user:
        raise HTTPException(detail="User not found by ID", status_code=status.HTTP_400_BAD_REQUEST)

    start = ayah_parts.get_ayah_part(db, recording_data.start, recording_data.riwayah)  # noqa
    end = ayah_parts.get_ayah_part(db, recording_data.end, recording_data.riwayah)  # noqa

    if not all([start, end]):
        message = ""
        if not start and not end:
            message = "Start and end ayah were not found."
        elif not start:
            message = "Start ayah was not found."
        elif not end:
            message = "End ayah was not found."
        raise HTTPException(detail=message, status_code=status.HTTP_400_BAD_REQUEST)

    audio_url = azure_blob_storage.upload_file(filename=f"audio_{uuid.uuid4()}.mp3", file=audio_file.file)

    return recordings_service.create_recording(db=db, user_id=user.id, start=start, end=end, audio_url=audio_url)


@recordings_router.delete("/{recording_id}")
def delete_recording(recording_id):
    pass


@recordings_router.post("/{recording_id}/share", response_model=SharedRecording)
def share_recording(
        share_data: RecordingShare,
        db: Session = db_session_dependency
):
    user = users_service.get_user_by_alias(db, share_data.recipient_alias)
    if not user:
        raise HTTPException(detail="User not found by alias", status_code=status.HTTP_400_BAD_REQUEST)

    recording = recordings_service.get_recording_by_id(db=db, recording_id=share_data.recording_id)
    if not recording:
        raise HTTPException(detail="Recording not found by ID", status_code=status.HTTP_400_BAD_REQUEST)
    elif recording.user_id == user.id:
        raise HTTPException(detail="Impossible to share recording with yourself",
                            status_code=status.HTTP_400_BAD_REQUEST)

    return recordings_service.share_recording(db=db, recording_id=share_data.recording_id, recipient_id=user.id)
