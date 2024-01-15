from datetime import datetime, timedelta

import jwt
from fastapi import HTTPException, Depends, status
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.config import MOBILE_APP_KEY, APP_PUBLIC_KEY, APP_PRIVATE_KEY, JWT_ALG
from src.dal.database import get_session
from src.dal.models import Token

API_KEY_HEADER = APIKeyHeader(name="X-API-Key")
ACCESS_JWT_BEARER = HTTPBearer()
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 90


async def verify_api_key(api_key: str = Depends(API_KEY_HEADER)):
    if api_key != MOBILE_APP_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access is forbidden",
        )
    return True


async def verify_access_token(
        credentials: HTTPAuthorizationCredentials = Depends(ACCESS_JWT_BEARER),
        db: Session = Depends(get_session)
):
    try:
        return is_token_correct(db=db, token=credentials.credentials)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def is_token_correct(db: Session, token: str) -> str:
    user_id = get_user_id_from_jwt(token)
    db_token = get_token(db, user_id)

    if (db_token is None) or (db_token.access_token != token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    return user_id


def get_user_id_from_jwt(token: str):
    payload = jwt.decode(token, APP_PUBLIC_KEY, algorithms=JWT_ALG)
    print(payload)
    return payload.get("user_id")


def generate_both_tokens(db: Session, user_id: str) -> (str, str):
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)
    db_token = get_token(db, user_id)

    if db_token is None:
        db_token = Token(user_id=user_id, access_token=access_token, refresh_token=refresh_token)
        db.add(db_token)
    else:
        db_token.access_token = access_token
        db_token.refresh_token = refresh_token

    db.commit()
    db.refresh(db_token)
    return access_token, refresh_token


def create_access_token(user_id: str) -> str:
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + expires_delta

    token = jwt.encode({"user_id": user_id, "exp": expire}, APP_PRIVATE_KEY, algorithm=JWT_ALG)
    return token


def refresh_access_token(db: Session, token: str) -> str:
    try:
        user_id = get_user_id_from_jwt(token)
        db_token = get_token(db, user_id)

        if (db_token is None) or (db_token.refresh_token != token):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        access_token = create_access_token(user_id)
        db_token.access_token = access_token

        db.commit()
        db.refresh(db_token)
        return access_token
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")


def create_refresh_token(user_id: str) -> str:
    expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    expire = datetime.utcnow() + expires_delta

    token = jwt.encode({"user_id": user_id, "exp": expire}, APP_PRIVATE_KEY, algorithm=JWT_ALG)
    return token


def get_token(db: Session, user_id: str) -> Token | None:
    return db.query(Token).filter_by(user_id=user_id).first()
