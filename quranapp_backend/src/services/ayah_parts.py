import uuid

from sqlalchemy.orm import Session, joinedload

from src.dal.enums import RiwayahEnum, PublisherEnum
from src.dal.models import AyahPart, Ayah
from src.models import AyahPartSearch


def get_ayah_part(
        db: Session, ayah_part_search_info: AyahPartSearch, riwayah: RiwayahEnum, publisher: PublisherEnum
) -> AyahPart | None:
    return db.query(AyahPart).filter(
        AyahPart.ayah.has(Ayah.mushaf.has(riwayah=riwayah)),
        AyahPart.ayah.has(Ayah.mushaf.has(publisher=publisher)),
        AyahPart.ayah.has(surah_number=ayah_part_search_info.surah_number),
        AyahPart.ayah.has(ayah_in_surah_number=ayah_part_search_info.ayah_in_surah_number),
        AyahPart.part_number == ayah_part_search_info.part_number
    ).first()


def get_extended_ayah_parts_by_mushaf_id(db: Session, mushaf_id: uuid.UUID) -> list[AyahPart]:
    return db.query(AyahPart).filter(AyahPart.ayah.has(mushaf_id=mushaf_id)).options(joinedload(AyahPart.ayah)).all()
