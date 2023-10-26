from sqlalchemy.orm import Session

from src.dal.models import AyahPart
from src.models import AyahPartSearch


def get_ayah_part(db: Session, ayah_part_search_info: AyahPartSearch) -> AyahPart | None:
    #todo add filtering by riwayah
    return db.query(AyahPart).filter(
        AyahPart.ayah.has(surah_number=ayah_part_search_info.surah_number),
        AyahPart.ayah.has(ayah_in_surah_number=ayah_part_search_info.ayah_in_surah_number),
        AyahPart.part_number == ayah_part_search_info.part_number
    ).first()

