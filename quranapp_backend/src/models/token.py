import uuid
from pydantic import BaseModel


class TokenRequest(BaseModel):
    app_id: uuid.UUID
    app_key: str



