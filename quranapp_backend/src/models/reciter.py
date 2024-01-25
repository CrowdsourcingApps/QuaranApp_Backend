import uuid

from pydantic import BaseModel

from src.dal.enums import RiwayahEnum


class Reciter(BaseModel):
    id: uuid.UUID
    name: str
    riwayah: RiwayahEnum
