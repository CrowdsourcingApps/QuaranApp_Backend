from pydantic import BaseModel


class User(BaseModel):
    id: int
    alias: str
