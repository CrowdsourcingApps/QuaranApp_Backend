import uuid

from pydantic import BaseModel

from src.models.ayah_part import MushafPageAyahPart


class MushafPage(BaseModel):
    id: uuid.UUID
    index: int
    mushaf_id: uuid.UUID
    light_mode_link: str
    dark_mode_link: str


class MushafPageDetails(BaseModel):
    page_id: uuid.UUID
    ayah_parts_count: int
    ayah_parts: list[MushafPageAyahPart]
