# tests/conftest.py
import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Add the project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

Base = declarative_base()


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
