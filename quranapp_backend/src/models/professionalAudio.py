from pydantic import BaseModel


class ProfessionalAudio(BaseModel):
    surahNumber: int
    ayahInSurahNumber: int
    url: str
