from fastapi import APIRouter, HTTPException, Depends
from src.models import UserModel
from src.services import users_service
from sqlalchemy.orm import Session
from .dependencies import get_db_session, transform_recording_data

user_router = APIRouter(
    prefix="/user",
    tags=["user"]
)


@user_router.get("/{user_id}", response_model=UserModel)
def get_user(user_id: str, db: Session = Depends(get_db_session)) -> UserModel:
    user = users_service.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail='User not found by ID')

    return user


@user_router.get("/find/{user_alias}", response_model=UserModel)
def find_user(user_alias: str, db: Session = Depends(get_db_session)) -> UserModel:
    user = users_service.get_user_by_alias(db, user_alias)
    if user is None:
        raise HTTPException(status_code=404, detail='User not found by Alias')

    return user


@user_router.get("/is-alias-available/{user_alias}")
def check_if_alias_exists(user_alias: str, db: Session = Depends(get_db_session)) -> bool:
    return users_service.check_if_alias_exists(db, user_alias)


@user_router.post("/create")
def create_user(user: UserModel, db: Session = Depends(get_db_session)) -> object:
    return users_service.create_user(db, user)
