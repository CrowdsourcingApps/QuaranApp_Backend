import json
import os

from sqlalchemy import insert
from sqlalchemy.orm import Session

from src.dal.enums import RiwayahEnum
from src.dal.models import AyahPart, Ayah


def fill_database_with_riwayah_data(session, file_name):
    data_directory = os.path.join(os.path.dirname(__file__), "data_files")
    with open(os.path.join(data_directory, file_name)) as f:
        initial_data = json.load(f)
        for riwayah, data in initial_data.items():
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


def delete_riwayah_data(session: Session, riwayah: RiwayahEnum):
    session.query(AyahPart).filter(AyahPart.ayah.has(riwayah=riwayah)).delete()
    session.query(Ayah).filter(Ayah.riwayah == riwayah).delete()
