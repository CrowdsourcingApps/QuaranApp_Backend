from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.services import tokens_service, UserService
from .dependencies import get_db_session

token_router = APIRouter(
    prefix="/token",
    tags=["token"]
)


@token_router.post("/generate")
def generate_jwt_token(user_id: str, _: str = Depends(tokens_service.get_api_key)):
    user = UserService.instance().get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail='Invalid user data')

    access_token = tokens_service.create_access_token(user_id)
    refresh_token = tokens_service.create_refresh_token(user_id)
    return {"access": access_token, "refresh": refresh_token}


@token_router.get("/check")
def check_access(api_key: str = Depends(tokens_service.get_api_key)):
    return api_key
