from pydantic import BaseModel


class AyahPartMarker(BaseModel):
    order: int
    x: int
    y1: int
    y2: int
    is_new_line: bool
