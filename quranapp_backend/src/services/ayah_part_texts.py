from sqlalchemy.orm import Session

from src.dal.models import AyahPartText


def get_all_ayah_part_texts(db: Session) -> list[AyahPartText]:
    return db.query(AyahPartText).all()
