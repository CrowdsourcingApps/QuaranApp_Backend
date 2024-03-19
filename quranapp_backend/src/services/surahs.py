import uuid
from typing import Type

from sqlalchemy.orm import Session

from src.dal.models import Surah, SurahInMushaf, MushafPage


def get_all_surahs(db: Session) -> list[Type[Surah]]:
    return db.query(Surah).all()


def get_surahs_in_mushaf(db: Session, mushaf_id: uuid.UUID):
    return db.query(SurahInMushaf) \
        .join(MushafPage, SurahInMushaf.first_page_id == MushafPage.id) \
        .filter(MushafPage.mushaf_id == mushaf_id) \
        .order_by(SurahInMushaf.surah_number) \
        .all()
