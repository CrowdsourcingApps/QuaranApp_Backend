from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.models import TokenRequest, BothTokensResponse
from src.services import tokens_service, users_service
from .dependencies import get_db_session

token_router = APIRouter(
    prefix="/token",
    tags=["token"]
)


@token_router.post("/generate", response_model=BothTokensResponse)
def generate_jwt_token(
        request: TokenRequest,
        db: Session = Depends(get_db_session),
        _: str = Depends(tokens_service.get_api_key)
):
    user = users_service.get_user_by_id(db, request.user_id)
    if user is None:
        raise HTTPException(status_code=401, detail='Invalid user data')
    return tokens_service.generate_both_tokens(db, user.id)


@token_router.get("/check")
def check_access(api_key: str = Depends(tokens_service.get_api_key)):
    return api_key
