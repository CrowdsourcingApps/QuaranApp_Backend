from sqlalchemy.orm import Session

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
