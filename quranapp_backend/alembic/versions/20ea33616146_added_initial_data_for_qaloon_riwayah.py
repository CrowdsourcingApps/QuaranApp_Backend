"""Added initial data for Qaloon riwayah

Revision ID: 20ea33616146
Revises: 815e860709a4
Create Date: 2023-12-24 21:06:03.735294

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session

from src.dal.enums import RiwayahEnum
from quran_data.db_actions import fill_database_with_riwayah_data, delete_riwayah_data


# revision identifiers, used by Alembic.
revision: str = '20ea33616146'
down_revision: Union[str, None] = '815e860709a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# сделал как тут: https://github.com/sqlalchemy/alembic/discussions/972#discussioncomment-1765978
def upgrade() -> None:
    with Session(op.get_bind()) as session:
        fill_database_with_riwayah_data(session, "initial_data_qaloon.json")


def downgrade() -> None:
    with Session(op.get_bind()) as session:
        delete_riwayah_data(session, RiwayahEnum.QALOON)
