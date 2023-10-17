import subprocess
from src.dal.database import SessionLocal


def apply_migrations():
    # Apply migrations
    with SessionLocal.begin() as session:
        try:
            subprocess.run(['alembic', 'upgrade', 'head'])
            print('\n\n[DB]\n\t----------- Migrations applied successfully !')
        except Exception as e:
            print('\n\n[DB]\n\t----------- Migrations failed ! ERROR : ', e)
