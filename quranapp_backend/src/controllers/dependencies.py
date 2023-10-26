from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError

from src.dal.database import SessionLocal
from src.models import RecordingCreate


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def transform_recording_data(recording_data: str) -> RecordingCreate:
    try:
        recording_data = RecordingCreate.model_validate_json(recording_data)
    except ValidationError as e:
        raise HTTPException(
            detail=jsonable_encoder(e.errors()),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    return recording_data
