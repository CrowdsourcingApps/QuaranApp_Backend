from fastapi import HTTPException
from sqlalchemy import or_, text
from sqlalchemy.orm import Session

import src.mappers as mapper
from src.dal.models import User
from src.models import UserModel, ApiMessageResponse


def get_user_by_id(db: Session, user_id: str) -> UserModel | None:
    user = db.get(User, user_id)
    if user is not None:
        db.expunge(user)
    return user


def get_user_by_alias(db: Session, alias: str) -> UserModel | None:
    formatted_alias = alias.strip().lower()
    user = db.query(User).filter_by(alias=formatted_alias).first()
    if user is not None:
        db.expunge(user)
    return user


def find_user_by_alias(db: Session, alias: str, user_id: str, count: int = 5) -> list[type(UserModel)]:
    prefix = alias.strip().lower()
    query = db.query(User).filter(
        or_(
            User.alias.like(text(':prefix')),  # noqa
            User.name.like(text(':prefix')),  # noqa
            User.surname.like(text(':prefix'))  # noqa
        ),
        User.id != user_id
    ).limit(count)

    result = query.params(prefix=f'{prefix}%').all()
    return result


def check_if_alias_exists(db: Session, alias: str) -> bool:
    formatted_alias = alias.strip().lower()
    return db.query(User.id).filter_by(alias=formatted_alias).first() is not None


def create_user(db: Session, user: UserModel) -> ApiMessageResponse:
    if check_if_alias_exists(db, user.alias):
        raise HTTPException(status_code=409, detail=f'Alias {user.alias} already in use.')

    if get_user_by_id(db, user.id) is not None:
        raise HTTPException(status_code=409, detail=f'ID already in use.')

    user_dal = mapper.user.map_to_dal(user)
    db.add(user_dal)
    db.commit()
    return ApiMessageResponse(message='User added successfully', is_success=True)


def delete_user(db: Session, user_id: str) -> bool:
    user = db.get(User, user_id)
    if user:
        db.delete(user)
        db.commit()
        return True
    return False
