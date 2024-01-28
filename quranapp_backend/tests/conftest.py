# tests/conftest.py
import os
import sys
import uuid
from typing import Any

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Add the project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

Base = declarative_base()
USER_1: Any = None
USER_2: Any = None


@pytest.fixture(scope="session")
def test_db_url():
    from src.config import db_url
    return db_url


@pytest.fixture(scope="session")
def engine(test_db_url):
    return create_engine(test_db_url)


@pytest.fixture(scope="session")
def tables(engine):
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(engine, tables):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def user1(db_session):
    global USER_1
    USER_1 = get_user(db_session, USER_1, 1)
    return USER_1


@pytest.fixture
def user2(db_session):
    global USER_2
    USER_2 = get_user(db_session, USER_2, 2)
    return USER_2


def get_user(db_session, user, user_index):
    from src.dal.models import User
    from src.services.users import create_user

    if user is not None:
        return user

    user_data = {
        'id': f'{uuid.uuid4()}_test',
        'alias': f'{uuid.uuid4()}_test_alias_{user_index}',
        'name': f'test_name_{user_index}',
        'surname': f'test_surname_{user_index}'}
    user = User(**user_data)

    create_user(db_session, user)
    return user


def pytest_unconfigure(config): # noqa
    from src.config import db_url
    from src.services.users import delete_user
    global USER_1, USER_2

    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # noqa
    db = SessionLocal()
    try:
        if USER_1 is not None:
            delete_user(db, USER_1.id)
        if USER_2 is not None:
            delete_user(db, USER_2.id)
    finally:
        db.close()
