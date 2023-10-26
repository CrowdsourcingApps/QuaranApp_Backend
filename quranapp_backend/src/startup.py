import uuid
import subprocess

from src.dal.database import SessionLocal
from src.dal.models import User, AyahPart


def apply_migrations():
    # Apply migrations
    with SessionLocal.begin() as session:
        try:
            subprocess.run(['alembic', 'upgrade', 'head'])
            print('\n\n[DB]\n\t----------- Migrations applied successfully !')
        except Exception as e:
            print('\n\n[DB]\n\t----------- Migrations failed ! ERROR : ', e)


def initial_database_fill():
    # Fill database with initial data
    with SessionLocal() as session:
        if session.query(User).count() == 0:
            user = User(id="some_str")
            session.add(user)
            print("Added user")
        #todo fix creation of ayah parts
        if session.query(AyahPart).count() == 0:
            ayah_part_1 = AyahPart(id=uuid.uuid4())
            ayah_part_2 = AyahPart(id=uuid.uuid4())
            session.add(ayah_part_1)
            session.add(ayah_part_2)
            print("Added ayah parts")
        session.commit()
