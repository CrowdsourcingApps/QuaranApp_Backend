import uuid
from datetime import datetime

from pydantic import BaseModel

from src.dal.enums import RiwayahEnum
from src.models.ayah_part import AyahPartSearch, AyahPart


class RecordingCreate(BaseModel):
    start: AyahPartSearch
    end: AyahPartSearch
    user_id: str  # возможно, пользователь будет передаваться как-то по-другому
    riwayah: RiwayahEnum


class Recording(BaseModel):
    id: uuid.UUID
    #todo user:
    start: AyahPart
    end: AyahPart
    audio_url: str
    created_at: datetime

    class Config:
        from_attributes = True
