import uuid
from datetime import datetime

from pydantic import BaseModel

from src.dal.enums import RiwayahEnum
from src.models.ayah_part import AyahPartDetailed, AyahPart, AyahPartSearch


class RecordingCreate(BaseModel):
    start: AyahPartSearch
    end: AyahPartSearch
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


class RecordingShare(BaseModel):
    recording_id: uuid.UUID
    recipient_alias: str


class SharedRecording(BaseModel):
    recording_id: uuid.UUID
    created_at: datetime


class DetailedRecording(BaseModel):
    user_alias: str
    riwayah: RiwayahEnum
    start: AyahPartDetailed
    end: AyahPartDetailed
    created_at: datetime
    audio_url: str
