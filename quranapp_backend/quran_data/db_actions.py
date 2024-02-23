import json
import os

from sqlalchemy import insert
from sqlalchemy.orm import Session

from src.dal.models import AyahPart, Ayah, Mushaf
from src.dal.utils import create_default_mushaf


# todo временные скрипты. Нужны для заполнения начальных данных по Ayah и AyahPart'ам, пока нет эндпоинта для
#  загрузки данных из файла. После появляния эндпоинта - скрипты можно удалить

# ================

def fill_database_with_initial_data_new(session, file_name):
    if session.query(Ayah).count() != 0 or session.query(AyahPart).count() != 0:
        return

    data_directory = os.path.join(os.path.dirname(__file__), "data_files")
    with open(os.path.join(data_directory, file_name)) as f:
        initial_data = json.load(f)
        mushaf = session.query(Mushaf).first()
        if not mushaf:
            mushaf = create_default_mushaf(session)

        for data in initial_data.values():
            for surah_number, ayah_count in data.items():
                ayah_data = list()
                for ayah_in_surah_number in range(ayah_count + 1):
                    ayah_data.append({
                        "mushaf_id": mushaf.id,
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


def delete_initial_data(session: Session):
    session.query(AyahPart).delete()
    session.query(Ayah).delete()
    session.commit()

# ================
