import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from src.dal.enums import RiwayahEnum, PublisherEnum
from src.models.ayah_part import AyahPartDetailed, AyahPart, AyahPartSearch


class RecordingCreate(BaseModel):
    riwayah: RiwayahEnum
    publisher: PublisherEnum
    start: AyahPartSearch
    end: AyahPartSearch


class Recording(BaseModel):
    id: uuid.UUID
    # todo user:
    start: AyahPart
    end: AyahPart
    audio_url: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RecordingShare(BaseModel):
    recording_id: uuid.UUID
    recipient_alias: str


class SharedRecording(BaseModel):
    recording_id: uuid.UUID
    created_at: datetime


class DetailedRecording(BaseModel):
    id: uuid.UUID
    user_alias: str
    is_my_recording: bool
    riwayah: RiwayahEnum
    publisher: PublisherEnum
    start: AyahPartDetailed
    start_page_index: int
    end: AyahPartDetailed
    end_page_index: int
    range_string: str
    created_at: datetime
    audio_url: str
