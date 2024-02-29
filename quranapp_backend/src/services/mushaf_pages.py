import uuid

from sqlalchemy.orm import Session

from src.dal.models import MushafPage


def get_pages_by_mushaf_id(db: Session, mushaf_id: uuid.UUID) -> list[MushafPage]:
    return db.query(MushafPage).filter_by(mushaf_id=mushaf_id).all()
