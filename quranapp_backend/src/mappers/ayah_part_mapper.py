import uuid

from src.dal.models import AyahPart as AyahPartDal
from src.dal.models import AyahPartMarker as AyahPartMarkerDal
from src.models import MushafPageDetails, MushafPageAyahPart, AyahPartMarker


def map_to_page_details(page_id: uuid.UUID, ayah_parts: list[AyahPartDal]) -> MushafPageDetails:
    mapped_ayah_parts = []
    for ayah_part in ayah_parts:
        mapped_ayah_parts.append(MushafPageAyahPart(
            id=ayah_part.id,
            part_number=ayah_part.part_number,
            surah_number=ayah_part.ayah.surah_number,
            ayah_in_surah_number=ayah_part.ayah.ayah_in_surah_number,
            text=ayah_part.text.text,
            text_id=ayah_part.ayah_part_text_id,
            markers=_map_ayah_part_markers(ayah_part.markers)
        ))

    return MushafPageDetails(
        page_id=page_id,
        ayah_parts_count=len(mapped_ayah_parts),
        ayah_parts=mapped_ayah_parts
    )


def _map_ayah_part_markers(markers: list[AyahPartMarkerDal]):
    mapped_markers = []
    for marker in markers:
        mapped_markers.append(AyahPartMarker(
            order=marker.order,
            x=marker.x,
            y1=marker.y1,
            y2=marker.y2,
            is_new_line=marker.is_new_line
        ))

    return sorted(mapped_markers, key=lambda m: m.order)
