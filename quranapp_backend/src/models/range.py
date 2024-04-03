import uuid

from pydantic import BaseModel

from src.dal.enums import PublisherEnum, RiwayahEnum
from src.models.partition import Partition


class Range(BaseModel):
    start: Partition
    end: Partition


class PagesRangeRequest(BaseModel):
    riwayah: RiwayahEnum
    publisher: PublisherEnum
    start_surah_number: int
    start_ayah_in_surah_number: int
    end_surah_number: int
    end_ayah_in_surah_number: int


class RangeStartAndEndPages(BaseModel):
    start_page_id: uuid.UUID
    start_page_index: int
    end_page_id: uuid.UUID
    end_page_index: int
