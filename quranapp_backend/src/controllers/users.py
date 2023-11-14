from fastapi import APIRouter, HTTPException
from src.models import UserModel
from src.services import UserService

user_router = APIRouter(
    prefix="/user",
    tags=["user"]
)


@user_router.get("/{user_id}", response_model=UserModel)
def get_user(user_id: str) -> UserModel:
    user = UserService.instance().get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail='User not found by ID')

    return user


@user_router.get("/find/{user_alias}", response_model=UserModel)
def find_user(user_alias: str) -> UserModel:
    user = UserService.instance().get_user_by_alias(user_alias)
    if user is None:
        raise HTTPException(status_code=404, detail='User not found by Alias')

    return user


@user_router.get("/is-alias-available/{user_alias}")
def check_if_alias_exists(user_alias: str) -> bool:
    return UserService.check_if_alias_exists(user_alias)


@user_router.post("/create")
def create_user(user: UserModel) -> object:
    return UserService.instance().create_user(user)
