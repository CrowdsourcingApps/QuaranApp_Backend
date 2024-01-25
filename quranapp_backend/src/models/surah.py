from pydantic import BaseModel


class Surah(BaseModel):
    id: int
    title: str
    revelation_type: str
    title_eng: str
    title_eng_translation: str
