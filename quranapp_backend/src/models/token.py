from pydantic import BaseModel


class TokenRequest(BaseModel):
    user_id: str


class TokensResponse(BaseModel):
    token: str
