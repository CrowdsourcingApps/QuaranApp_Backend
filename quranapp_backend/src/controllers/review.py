import uuid

from fastapi import APIRouter
from sqlalchemy.orm import Session

from src.controllers.dependencies import db_session_dependency, api_key_dependency, jwt_dependency
from src.models import MistakesRequest, ApiMessageResponse, MistakeMarkerInformation
from src.services import review_service, recordings as recordings_service

review_router = APIRouter(
    prefix="/review",
    tags=["review"],
    dependencies=[api_key_dependency]
)


@review_router.post("/{recording_id}", response_model=ApiMessageResponse)
def upload_review_for_recording(
        recording_id: uuid.UUID,
        mistakes_request: MistakesRequest,
        user_id: str = jwt_dependency,
        db: Session = db_session_dependency
):
    recordings_service.mark_as_reviewed(db=db, recipient_id=user_id, recording_id=recording_id)

    review_service.upload_review(
        db=db, recording_id=recording_id, commentator_id=user_id, mistakes=mistakes_request.mistakes)

    return ApiMessageResponse(message='Review uploaded successfully', is_success=True)


@review_router.get("/recording_id", response_model=list[MistakeMarkerInformation])
def get_reviews_for_recording(
        recording_id: uuid.UUID,
        user_id: str = jwt_dependency,
        db: Session = db_session_dependency
):
    recordings_service.check_recording_access(db=db, user_id=user_id, recording_id=recording_id)
    return review_service.get_reviews(db=db, recording_id=recording_id)
