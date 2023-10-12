import os


DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
DB_HOST_NAME = os.environ.get('DB_HOST')
DB_NAME = os.environ.get('POSTGRES_DB')

db_url = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST_NAME}/{DB_NAME}'

print("DB_HOST:  ", DB_HOST_NAME)
print("db_url:  ", db_url)
