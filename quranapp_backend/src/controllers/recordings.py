import uuid

from fastapi import APIRouter, UploadFile, HTTPException, status, File, Form
from sqlalchemy.orm import Session

import src.mappers as mapper
from src.controllers.dependencies import db_session_dependency, api_key_dependency, jwt_dependency
from src.dal.enums import RiwayahEnum, PublisherEnum
from src.models import Recording, RecordingShare, SharedRecording, DetailedRecording, ApiMessageResponse
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
        riwayah: RiwayahEnum = Form(),
        publisher: PublisherEnum = Form("MADINA"),
        start_surah_number: int = Form(),
        start_ayah_in_surah_number: int = Form(),
        start_part_number: int = Form(0),
        end_surah_number: int = Form(),
        end_ayah_in_surah_number: int = Form(),
        end_part_number: int = Form(0),
        audio_file: UploadFile = File(),
        user_id: str = jwt_dependency,
        db: Session = db_session_dependency
):
    recording_data = mapper.recording.map_create_request_to_model(
        start_surah_number, start_ayah_in_surah_number,
        start_part_number, end_surah_number,
        end_ayah_in_surah_number, end_part_number, riwayah, publisher
    )

    user = users_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(detail="User not found by ID", status_code=status.HTTP_400_BAD_REQUEST)

    start = ayah_parts.get_ayah_part(db, recording_data.start, recording_data.riwayah, recording_data.publisher)
    end = ayah_parts.get_ayah_part(db, recording_data.end, recording_data.riwayah, recording_data.publisher)

    if not all([start, end]):
        message = ""
        if not start and not end:
            message = "Start and end ayah were not found."
        elif not start:
            message = "Start ayah was not found."
        elif not end:
            message = "End ayah was not found."
        raise HTTPException(detail=message, status_code=status.HTTP_400_BAD_REQUEST)

    audio_url = azure_blob_storage.upload_file(filename=audio_file.filename, file=audio_file.file)

    return recordings_service.create_recording(db=db, user_id=user_id, start=start, end=end, audio_url=audio_url)


@recordings_router.delete("/{recording_id}", response_model=ApiMessageResponse)
def delete_recording(recording_id: uuid.UUID, user_id: str = jwt_dependency, db: Session = db_session_dependency):
    recordings_service.check_recording_owner(db=db, user_id=user_id, recording_id=recording_id)
    recordings_service.delete_recording(db=db, recording_id=recording_id)
    return ApiMessageResponse(message='Recording deleted successfully', is_success=True)


@recordings_router.post("/{recording_id}/share", response_model=SharedRecording)
def share_recording(
        share_data: RecordingShare,
        user_id: str = jwt_dependency,
        db: Session = db_session_dependency
):
    recordings_service.check_recording_owner(db=db, user_id=user_id, recording_id=share_data.recording_id)
    user = users_service.get_user_by_alias(db, share_data.recipient_alias)
    if not user:
        raise HTTPException(detail="User not found by alias", status_code=status.HTTP_400_BAD_REQUEST)

    recording = recordings_service.get_recording_by_id(db=db, recording_id=share_data.recording_id)
    if recording.user_id == user.id:
        raise HTTPException(detail="Impossible to share recording with yourself",
                            status_code=status.HTTP_400_BAD_REQUEST)

    return recordings_service.share_recording(db=db, recording_id=share_data.recording_id, recipient_id=user.id)
