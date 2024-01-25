from fastapi import APIRouter
from sqlalchemy.orm import Session

from src.controllers.dependencies import db_session_dependency
from src.models import Surah
from src.services import surahs_service

quran_router = APIRouter(
    prefix="/quran",
    tags=["quran"]
)


@quran_router.get("/surahs", response_model=list[Surah])
def get_all_surahs(db: Session = db_session_dependency):
    return surahs_service.get_all_surahs(db)
