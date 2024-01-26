from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

import src.config as AppConfig

# Поменять здесь при настройке Postgres в Docker
SQLALCHEMY_DATABASE_URL = AppConfig.db_url
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
