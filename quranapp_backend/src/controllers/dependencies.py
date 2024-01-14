from fastapi import HTTPException, status, Depends
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError

from src.dal.database import get_session
from src.models import RecordingCreate
from src.services import tokens_service


api_key_dependency = Depends(tokens_service.verify_api_key)
jwt_dependency = Depends(tokens_service.verify_access_token)
db_session_dependency = Depends(get_session)


def transform_recording_data(recording_data: str) -> RecordingCreate:
    try:
        recording_data = RecordingCreate.model_validate_json(recording_data)
    except ValidationError as e:
        raise HTTPException(
            detail=jsonable_encoder(e.errors()),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    return recording_data
