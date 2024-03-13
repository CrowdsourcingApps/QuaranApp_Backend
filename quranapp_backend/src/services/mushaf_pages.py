import uuid

from sqlalchemy.orm import Session

from src.dal.models import MushafPage, Ayah, AyahPart, AyahPartMarker, AyahPartText
from src.mappers import ayah_part_mapper
from src.models import MushafPageDetails


def get_pages_by_mushaf_id(db: Session, mushaf_id: uuid.UUID) -> list[MushafPage]:
    return db.query(MushafPage).filter_by(mushaf_id=mushaf_id).all()


def get_ayah_parts_and_markers_by_page_id(db: Session, page_id: uuid.UUID) -> MushafPageDetails:
    ayah_parts = db.query(AyahPart) \
            .join(AyahPartMarker, AyahPart.id == AyahPartMarker.ayah_part_id) \
            .join(Ayah, Ayah.id == AyahPart.ayah_id) \
            .filter(AyahPart.mushaf_page_id == page_id) \
            .order_by(Ayah.surah_number, Ayah.ayah_in_surah_number) \
            .all()

    return ayah_part_mapper.map_to_page_details(page_id=page_id, ayah_parts=ayah_parts)
