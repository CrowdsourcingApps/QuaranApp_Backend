FROM python:3.11-slim-bullseye as build

COPY . /app

RUN apt-get update --fix-missing && apt-get install build-essential libpq-dev -y

WORKDIR /app/quranapp_backend

RUN pip install --no-cache-dir --upgrade -r requirements.txt

FROM build AS runtime

EXPOSE $PORT

CMD uvicorn main:app --host 0.0.0.0 --port $PORT