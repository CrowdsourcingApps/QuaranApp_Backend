from fastapi import APIRouter, HTTPException, Response, Request
from sqlalchemy.orm import Session

from src.controllers.dependencies import db_session_dependency, jwt_dependency, api_key_dependency
from src.models import TokenRequest, TokensResponse
from src.services import tokens_service, users_service

token_router = APIRouter(
    prefix="/token",
    tags=["token"],
    dependencies=[api_key_dependency]
)


@token_router.post("/generate", response_model=TokensResponse)
def generate_jwt_token(
        request: TokenRequest,
        response: Response,
        db: Session = db_session_dependency
):
    user = users_service.get_user_by_id(db, request.user_id)
    if user is None:
        raise HTTPException(status_code=401, detail='Invalid user data')

    access_token, refresh_token = tokens_service.generate_both_tokens(db, user.id)
    response.set_cookie(key="refresh_token", value=refresh_token)
    return TokensResponse(token=access_token)


@token_router.get("/refresh")
def get_cookie(request: Request, db: Session = db_session_dependency):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail='Invalid user data')

    return tokens_service.refresh_access_token(db=db, token=refresh_token)
