import uuid

from sqlalchemy.orm import Session

from src.dal.models import Ayah


def get_ayahs_by_mushaf_id(db: Session, mushaf_id: uuid.UUID) -> list[Ayah]:
    return db.query(Ayah).filter_by(mushaf_id=mushaf_id).all()
