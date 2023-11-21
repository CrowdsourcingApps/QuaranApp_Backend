import os
import json
import subprocess

from sqlalchemy import insert

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


def initial_db_fill():
    # Fill database with initial data
    with SessionLocal() as session:
        if session.query(User).count() == 0:
            user = User(name="Test", alias="test", surname="Testov", id="1")
            session.add(user)
            session.commit()
        fill_db_with_ayahs_and_ayah_parts_data(session)
        print("\n\n[DB]\n\t----------- Database is filled with initial data")


def fill_db_with_ayahs_and_ayah_parts_data(session):
    initial_data_directory = os.path.dirname(os.path.dirname(__file__))
    try:
        with open(os.path.join(initial_data_directory, "initial_data.json")) as f:
            initial_data = json.load(f)
            for riwayah, data in initial_data.items():
                if not session.query(Ayah).filter(Ayah.riwayah == riwayah).count():

                    for surah_number, ayah_count in data.items():
                        ayah_data = list()
                        for ayah_in_surah_number in range(1, ayah_count+1):
                            ayah_data.append({
                                "riwayah": riwayah,
                                 "surah_number": surah_number,
                                 "ayah_in_surah_number": ayah_in_surah_number
                            })

                        ayahs = session.scalars(
                            insert(Ayah).returning(Ayah),
                            ayah_data
                        )
                        session.commit()

                        ayah_part_data = list()
                        for ayah in ayahs:
                            ayah_part_data.append({
                                "ayah_id": ayah.id,
                                "part_number": 0
                            })

                        session.execute(
                            insert(AyahPart),
                            ayah_part_data
                        )
                        session.commit()

    except FileNotFoundError:
        print("File 'initial_data.json' not found.")
