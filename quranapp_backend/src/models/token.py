from pydantic import BaseModel


class TokenRequest(BaseModel):
    user_id: str


class BothTokensResponse(BaseModel):
    access_token: str
    refresh_token: str
