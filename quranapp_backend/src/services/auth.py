from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from src.config import MOBILE_APP_KEY, APP_PUBLIC_KEY, APP_PRIVATE_KEY, JWT_ALG
from src.dal.models import Token
from src.models import BothTokensResponse

import jwt


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


def generate_both_tokens(db: Session, user_id: str) -> BothTokensResponse:
    access_token, access_expire = create_access_token(user_id)
    refresh_token, refresh_expire = create_refresh_token(user_id)
    db_token = get_tokens(db, user_id)

    if db_token is None:
        db_token = Token(user_id=user_id, access_token=access_token, refresh_token=refresh_token,
                         access_token_expires=access_expire, refresh_token_expires=refresh_expire)
        db.add(db_token)
    else:
        db_token.access_token = access_token
        db_token.access_token_expires = access_expire
        db_token.refresh_token = refresh_token
        db_token.refresh_token_expires = refresh_expire

    db.commit()
    db.refresh(db_token)
    return BothTokensResponse(access_token=access_token, refresh_token=refresh_token)


def create_access_token(user_id: str) -> (str, datetime):
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + expires_delta
    expire_str = str(expire)

    token = jwt.encode({"user_id": user_id, "expire": expire_str}, APP_PRIVATE_KEY, algorithm=JWT_ALG)
    return token, expire


def create_refresh_token(user_id: str) -> (str, datetime):
    expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    expire = datetime.utcnow() + expires_delta
    expire_str = str(expire)

    token = jwt.encode({"user_id": user_id, "expire": expire_str}, APP_PRIVATE_KEY, algorithm=JWT_ALG)
    return token, expire


def get_tokens(db: Session, user_id: str) -> Token | None:
    return db.query(Token).filter_by(user_id=user_id).first()
