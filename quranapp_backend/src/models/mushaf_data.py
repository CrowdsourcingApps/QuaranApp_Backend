from pydantic import BaseModel, Field

from src.dal.enums import RiwayahEnum, PublisherEnum


class AyahPartMarkerData(BaseModel):
    x: int
    y1: int
    y2: int


class AyahPartData(BaseModel):
    page_number: int
    surah_number: int
    ayah_number: int
    part_number: int = 0
    text: str | None = None
    lines: list[list[AyahPartMarkerData]]


class MushafData(BaseModel):
    riwayah: RiwayahEnum
    publisher: PublisherEnum
    ayah_parts_data: list[AyahPartData] = Field(alias="ayahParts")
