import uuid

from pydantic import BaseModel


class AyahPartDetailed(BaseModel):
    surah_number: int
    ayah_in_surah_number: int
    part_number: int = 0


class AyahPart(BaseModel):
    id: uuid.UUID
