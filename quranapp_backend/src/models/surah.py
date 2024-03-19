import uuid

from pydantic import BaseModel


class Surah(BaseModel):
    id: int
    title: str
    revelation_type: str
    title_eng: str
    title_eng_translation: str


class SurahInMushaf(BaseModel):
    first_page_id: uuid.UUID
    surah_number: int
