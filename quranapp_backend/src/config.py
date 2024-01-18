import os

DB_USER = "myuser" if os.getenv('POSTGRES_USER') is None else os.getenv('POSTGRES_USER')
DB_PASSWORD = "mypassword" if os.environ.get('POSTGRES_PASSWORD') is None else os.environ.get('POSTGRES_PASSWORD')
DB_HOST_NAME = "localhost" if os.environ.get('DB_HOST') is None else os.environ.get('DB_HOST')
DB_NAME = "mydatabase" if os.environ.get('POSTGRES_DB') is None else os.environ.get('POSTGRES_DB')
DB_SSL = "disable" if os.environ.get('DB_SSL') is None else os.environ.get('DB_SSL')
MOBILE_APP_KEY = "key" if os.environ.get('MOBILE_APP_KEY') is None else os.environ.get('MOBILE_APP_KEY')
APP_PUBLIC_KEY = b"key" if os.environ.get('APP_PUBLIC_KEY') is None else bytes(
    os.environ.get('APP_PUBLIC_KEY').replace('\\n', '\n'), 'UTF-8')
APP_PRIVATE_KEY = b"key" if os.environ.get('APP_PRIVATE_KEY') is None else bytes(
    os.environ.get('APP_PRIVATE_KEY').replace('\\n', '\n'), 'UTF-8')
JWT_ALG = "RS512" if os.environ.get('JWT_ALG') is None else os.environ.get('JWT_ALG')

db_url = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST_NAME}/{DB_NAME}?sslmode={DB_SSL}'

print("DB_HOST:  ", DB_HOST_NAME)
print("SSL TYPE:", DB_SSL)
