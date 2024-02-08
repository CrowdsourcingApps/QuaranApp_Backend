"""Added initial data for ayahs and ayah_parts tables - temporary migration

Revision ID: 4f8f162de84b
Revises: 144a5671307f
Create Date: 2024-02-08 15:50:24.937657

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session

from quran_data.db_actions import fill_database_with_initial_data_new, delete_initial_data


# revision identifiers, used by Alembic.
revision: str = '4f8f162de84b'
down_revision: Union[str, None] = '144a5671307f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# todo временная миграция. Нужна для заполнения начальных данных по Ayah и AyahPart'ам, пока нет эндпоинта для
#  загрузки данных из файла. После появляния эндпоинта - миграцию можно удалить

def upgrade() -> None:
    with Session(op.get_bind()) as session:
        fill_database_with_initial_data_new(session, "initial_data_qaloon.json")


def downgrade() -> None:
    with Session(op.get_bind()) as session:
        delete_initial_data(session)
