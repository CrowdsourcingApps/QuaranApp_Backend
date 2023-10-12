from fastapi import APIRouter
from src.DAL.database import SessionLocal
from sqlalchemy import text

settings_router = APIRouter(
    prefix="/settings",
    tags=["settings"]
)


@settings_router.get("/ping_db")
def get_ping_db():
    with SessionLocal.begin() as session:
        try:
            session.execute(text('SELECT 1'))
            print('\n\n----------- Connection successful !')
        except Exception as e:
            print('\n\n----------- Connection failed ! ERROR : ', e)
