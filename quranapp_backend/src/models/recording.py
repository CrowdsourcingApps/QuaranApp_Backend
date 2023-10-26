import uuid
from datetime import datetime

from pydantic import BaseModel

from .ayah_part import AyahPartSearch, AyahPart


class RecordingCreate(BaseModel):
    start: AyahPartSearch
    end: AyahPartSearch
    user_id: str #возможно, пользователь будет передаваться как-то по-другому


class Recording(BaseModel):
    id: uuid.UUID
    #user:
    start: AyahPart
    end: AyahPart
    audio_url: str
    created_at: datetime

    class Config:
        from_attributes = True
