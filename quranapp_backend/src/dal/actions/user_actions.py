from src.dal.database import SessionLocal
from src.dal.models import User
def check_alias_exists(user_alias: str):
    with SessionLocal.begin() as session:
        result = session.query(User.id).filter_by(alias=user_alias).first() is not None
        return result
def get_user_by_id(user_id: str):
    with SessionLocal.begin() as session:
        result = session.query(User).get(user_id)
        if result is not None:
            session.expunge(result)
        return result
def get_user_by_alias(user_alias: str):
    with SessionLocal.begin() as session:
        result = session.query(User).filter_by(alias=user_alias).first()
        if result is not None:
            session.expunge(result)
        return result
def add_user(user: User):
    with SessionLocal.begin() as session:
        session.add(user)
        session.commit()