import os


DB_USER = "myuser" if os.getenv('POSTGRES_USER') is None else os.getenv('POSTGRES_USER')
DB_PASSWORD = "mypassword" if os.environ.get('POSTGRES_PASSWORD') is None else os.environ.get('POSTGRES_PASSWORD')
DB_HOST_NAME = "localhost" if os.environ.get('DB_HOST') is None else os.environ.get('DB_HOST')
DB_NAME = "mydatabase" if os.environ.get('POSTGRES_DB') is None else os.environ.get('POSTGRES_DB')
DB_SSL = "disable" if os.environ.get('DB_SSL') is None else os.environ.get('DB_SSL')

db_url = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST_NAME}/{DB_NAME}?sslmode={DB_SSL}'

print("DB_HOST:  ", DB_HOST_NAME)
print("SSD TYPE:", DB_SSL)
