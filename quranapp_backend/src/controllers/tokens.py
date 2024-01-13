from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session

from src.models import TokenRequest, TokensResponse
from src.services import tokens_service, users_service
from .dependencies import get_db_session

token_router = APIRouter(
    prefix="/token",
    tags=["token"]
)


@token_router.post("/generate", response_model=TokensResponse)
def generate_jwt_token(
        request: TokenRequest,
        response: Response,
        db: Session = Depends(get_db_session),
        _: str = Depends(tokens_service.verify_api_key)
):
    user = users_service.get_user_by_id(db, request.user_id)
    if user is None:
        raise HTTPException(status_code=401, detail='Invalid user data')

    access_token, refresh_token = tokens_service.generate_both_tokens(db, user.id)
    response.set_cookie(key="refresh_token", value=refresh_token)
    return TokensResponse(token=access_token)


@token_router.get("/refresh")
def get_cookie(request: Request, db: Session = Depends(get_db_session),):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail='Invalid user data')

    return tokens_service.refresh_access_token(db=db, token=refresh_token)


@token_router.get("/check-jwt-access")
def protected_route(is_correct: bool = Depends(tokens_service.verify_access_token)):
    return is_correct


@token_router.get("/check-api-key")
def check_access(is_correct: bool = Depends(tokens_service.verify_api_key)):
    return is_correct
