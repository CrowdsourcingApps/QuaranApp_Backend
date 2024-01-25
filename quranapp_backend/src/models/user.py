from pydantic import BaseModel


class User(BaseModel):
    id: str
    alias: str
    name: str
    surname: str
