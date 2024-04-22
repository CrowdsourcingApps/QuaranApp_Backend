import uuid

from sqlalchemy.orm import Session, joinedload

from src.dal.enums import RiwayahEnum
from src.dal.models import Reciter, ReciterAudio


def get_reciter(db: Session, name: str, riwayah: RiwayahEnum) -> Reciter | None:
    reciter = db.query(Reciter).filter_by(name=name, riwayah=riwayah).first()
    if reciter is not None:
        db.expunge(reciter)
    return reciter


def create_reciter(db: Session, name: str, riwayah: RiwayahEnum) -> Reciter:
    db_reciter = Reciter(name=name, riwayah=riwayah)
    db.add(db_reciter)
    db.commit()
    db.refresh(db_reciter)
    return db_reciter


def get_or_create_reciter(db: Session, name: str, riwayah: RiwayahEnum) -> Reciter:
    reciter = get_reciter(db, name, riwayah)
    if not reciter:
        reciter = create_reciter(db, name, riwayah)
    return reciter


def get_reciter_audios_by_reciter_id(db: Session, reciter_id: uuid.UUID) -> list[ReciterAudio]:
    return db.query(ReciterAudio).filter_by(reciter_id=reciter_id).all()

