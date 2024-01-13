from datetime import datetime, timedelta

from fastapi import HTTPException, Depends, status
from fastapi.security import APIKeyHeader
from src.config import MOBILE_APP_KEY, APP_PUBLIC_KEY, APP_PRIVATE_KEY, JWT_ALG
import jwt
import uuid


API_KEY = APIKeyHeader(name="X-API-Key")
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30


async def get_api_key(api_key: str = Depends(API_KEY)):
    if api_key != MOBILE_APP_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access is forbidden",
        )
    return api_key


def create_access_token(user_id: str) -> str:
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + expires_delta
    expire_str = str(expire)

    token = jwt.encode({"user_id": user_id, "expire": expire_str}, APP_PRIVATE_KEY, algorithm=JWT_ALG)
    return token


def create_refresh_token(user_id: str) -> str:
    expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    expire = datetime.utcnow() + expires_delta
    expire_str = str(expire)

    encoded_jwt = jwt.encode({"user_id": user_id, "expire": expire_str}, APP_PRIVATE_KEY, algorithm=JWT_ALG)
    return encoded_jwt
