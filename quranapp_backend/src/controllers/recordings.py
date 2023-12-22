import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, HTTPException, status
from sqlalchemy.orm import Session


from src.services import azure_blob_storage, recordings as recordings_service, ayah_parts, user_service
from src.models import Recording
from .dependencies import get_db_session, transform_recording_data

recordings_router = APIRouter(
    prefix="/recordings",
    tags=["recordings"]
)


@recordings_router.get("/my/{user_id}", response_model=list[Recording])
def get_my_recordings(user_id: str, db: Session = Depends(get_db_session)):
    user = UserService.instance().get_user_by_id(user_id)  # noqa
    if not user:
        raise HTTPException(detail="User not found by ID", status_code=status.HTTP_400_BAD_REQUEST)
    return recordings_service.get_my_recordings(db, user.id)


@recordings_router.get("/shared_with_me/{user_id}")
def get_shared_recordings(user_id: str, db: Session = Depends(get_db_session)):
    pass


@recordings_router.post("/upload", response_model=Recording)
def upload_recording(
        audio_file: UploadFile,
        recording_data: Annotated[str, Depends(transform_recording_data)],
        db: Session = Depends(get_db_session)
):
    user = user_service.UserService.instance().get_user_by_id(recording_data.user_id)
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


@recordings_router.post("/{recording_id}/share")
def share_recording(recording_id):
    pass
