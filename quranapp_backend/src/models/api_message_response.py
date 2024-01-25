from pydantic import BaseModel


class ApiMessageResponse(BaseModel):
    message: str
    is_success: bool
