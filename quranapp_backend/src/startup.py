import subprocess

from src.dal.database import SessionLocal
from src.dal.enums import RiwayahEnum
from src.dal.models import User, AyahPart, Ayah


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
        if session.query(User).count() == 0 and session.query(AyahPart).count() == 0 and session.query(Ayah).count() == 0:
            user = User(name="Test", alias="test", surname="Testov", id="1")
            session.add(user)
            ayah = Ayah(surah_number=1, ayah_in_surah_number=2, riwayah=RiwayahEnum.QALOON)
            session.add(ayah)
            ayah_part1 = AyahPart(ayah=ayah, part_number=0)
            ayah_part2 = AyahPart(ayah=ayah, part_number=1)
            session.add(ayah_part1)
            session.add(ayah_part2)
            session.commit()
            print("Added user, ayah and ayah parts initial data")
