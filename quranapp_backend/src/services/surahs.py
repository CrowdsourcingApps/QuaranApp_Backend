from typing import Type

from sqlalchemy.orm import Session
from src.dal.models import Surah


def get_all_surahs(db: Session) -> list[Type[Surah]]:
    return db.query(Surah).all()
