from fastapi import HTTPException
from sqlalchemy.orm import Session

import src.mappers as mapper
from src.dal.models import User
from src.models import UserModel, ApiMessageResponse


def get_user_by_id(db: Session, user_id: str) -> UserModel | None:
    user = db.query(User).get(user_id)
    if user is not None:
        db.expunge(user)
    return user


def get_user_by_alias(db: Session, alias: str) -> UserModel | None:
    user = db.query(User).filter_by(alias=alias).first()
    if user is not None:
        db.expunge(user)
    return user


def check_if_alias_exists(db: Session, alias: str) -> bool:
    return db.query(User.id).filter_by(alias=alias).first() is not None


def create_user(db: Session, user: UserModel) -> ApiMessageResponse:
    if check_if_alias_exists(db, user.alias):
        raise HTTPException(status_code=409, detail=f'Alias {user.alias} already in use.')

    if get_user_by_id(db, user.id) is not None:
        raise HTTPException(status_code=409, detail=f'ID already in use.')

    user_dal = mapper.user.map_to_dal(user)
    db.add(user_dal)
    db.commit()
    return ApiMessageResponse(message='User added successfully', is_success=True)
