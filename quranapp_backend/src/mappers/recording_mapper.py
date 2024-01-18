from src.dal.enums import RiwayahEnum
from src.models import AyahPartSearch, RecordingCreate


def map_create_request_to_model(
        start_surah_number: int, start_ayah_in_surah_number: int,
        start_part_number: int,
        end_surah_number: int,
        end_ayah_in_surah_number: int,
        end_part_number: int,
        riwayah: RiwayahEnum
) -> RecordingCreate:
    return RecordingCreate(
        start=AyahPartSearch(
            surah_number=start_surah_number,
            ayah_in_surah_number=start_ayah_in_surah_number,
            part_number=start_part_number),
        end=AyahPartSearch(
            surah_number=end_surah_number,
            ayah_in_surah_number=end_ayah_in_surah_number,
            part_number=end_part_number),
        riwayah=riwayah
    )
