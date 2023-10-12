from fastapi import APIRouter
from src.models import User

user_router = APIRouter(
    prefix="/user",
    tags=["user"]
)


@user_router.get("/{user_id}")
def get_user(user_id: int):
    return {"message": f"Get user with ID: {user_id}"}


@user_router.get("/find/{user_alias}")
def find_user(user_alias: str):
    return {"message": f"Find user with alias: {user_alias}"}


@user_router.post("/create")
def create_user(user: User):
    return {"message": "Add new user"}
