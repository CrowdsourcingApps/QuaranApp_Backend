import uuid

from pydantic import BaseModel


class AyahPartBase(BaseModel):
    surah_number: int
    ayah_in_surah_number: int
    part_number: int = 0


class AyahPartSearch(AyahPartBase):
    pass


class AyahPartDetailed(AyahPartBase):
    pass


class AyahPart(BaseModel):
    id: uuid.UUID
