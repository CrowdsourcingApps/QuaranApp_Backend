from pydantic import BaseModel

from src.models.partition import Partition


class Range(BaseModel):
    start: Partition
    end: Partition
