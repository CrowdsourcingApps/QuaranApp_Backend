# QuaranApp Backend

## MVP v.1

### DB Diagram

### Создание и применение миграций
Для создания миграций нужно находиться в одной директории с файлом alembic.ini.

Создание новой миграции:


`alembic revision --autogenerate -m "Название миграции"
`

Применение миграции:

`alembic upgrade head`