from pydantic import BaseModel


class Partition(BaseModel):
    surahNumber: int
    ayahInSurahNumber: int
    partNumber: int
