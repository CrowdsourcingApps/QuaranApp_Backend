from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from src.controllers.dependencies import db_session_dependency, api_key_dependency
from src.models import UserModel
from src.services import users_service

user_router = APIRouter(
    prefix="/user",
    tags=["user"],
    dependencies=[api_key_dependency]
)


@user_router.get("/{user_id}", response_model=UserModel)
def get_user(user_id: str, db: Session = db_session_dependency) -> UserModel:
    user = users_service.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail='User not found by ID')

    return user


@user_router.get("/find/{user_alias}", response_model=UserModel)
def find_user(user_alias: str, db: Session = db_session_dependency) -> UserModel:
    user = users_service.get_user_by_alias(db, user_alias)
    if user is None:
        raise HTTPException(status_code=404, detail='User not found by Alias')

    return user


@user_router.get("/is-alias-available/{user_alias}")
def check_if_alias_exists(
        user_alias: str,
        db: Session = db_session_dependency
) -> bool:
    return users_service.check_if_alias_exists(db, user_alias)


@user_router.post("/create")
def create_user(
        user: UserModel,
        db: Session = db_session_dependency
) -> object:
    return users_service.create_user(db, user)
