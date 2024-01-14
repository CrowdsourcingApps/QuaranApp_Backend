from fastapi import APIRouter

from src.controllers.dependencies import jwt_dependency, api_key_dependency
from src.dal.database import SessionLocal
from sqlalchemy import text

settings_router = APIRouter(
    prefix="/settings",
    tags=["settings"]
)


@settings_router.get("/ping_db")
def get_ping_db(_: bool = api_key_dependency):
    with SessionLocal.begin() as session:
        try:
            session.execute(text('SELECT 1'))
            print('\n\n----------- Connection successful !')
        except Exception as e:
            print('\n\n----------- Connection failed ! ERROR : ', e)
    return "Connection successful"


@settings_router.get("/200")
def get_ok(_: bool = api_key_dependency):
    return True


@settings_router.get("/check-jwt-access")
def protected_route(is_correct: bool = jwt_dependency):
    return is_correct


@settings_router.get("/check-api-key")
def check_access(is_correct: bool = api_key_dependency):
    return is_correct
