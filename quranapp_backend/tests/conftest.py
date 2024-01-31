# tests/conftest.py
import os
import sys
import pytest

# Add the project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def db_session():
    from src.dal.database import SessionLocal

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
