from sqlalchemy.orm import Session

from src.dal.enums import RiwayahEnum, PublisherEnum
from src.dal.models import Mushaf, Ayah


def create_default_mushaf(session: Session) -> Mushaf:
    db_mushaf = Mushaf(publisher=PublisherEnum.MADINA, riwayah=RiwayahEnum.QALOON)
    session.add(db_mushaf)
    session.commit()
    session.refresh(db_mushaf)
    return db_mushaf


def fill_mushaf_for_existing_ayahs(session: Session):
    mushaf = create_default_mushaf(session)
    session.query(Ayah).update({"mushaf_id": mushaf.id})
    session.commit()
