import uuid
from typing import Type

from sqlalchemy.orm import Session, joinedload

from src.dal.models import Surah, SurahInMushaf, MushafPage
from src.mappers import surahs_in_mushaf_mapper


def get_all_surahs(db: Session) -> list[Type[Surah]]:
    return db.query(Surah).all()


def get_surahs_in_mushaf(db: Session, mushaf_id: uuid.UUID):
    surahs_in_mushaf = (db.query(SurahInMushaf)
            .join(MushafPage, SurahInMushaf.first_page_id == MushafPage.id)
            .filter(MushafPage.mushaf_id == mushaf_id)
            .options(joinedload(SurahInMushaf.surah).joinedload(Surah.ayahs), joinedload(SurahInMushaf.mushaf_page))
            .order_by(SurahInMushaf.surah_number)
            .all())

    print(surahs_in_mushaf)

    return surahs_in_mushaf_mapper.map_surahs_in_mushaf(surahs_in_mushaf)
