FROM ubuntu:latest as build

COPY . /app

RUN apt-get update && apt-get install -y python3.11 python3-pip build-essential libpq-dev

WORKDIR /app/quranapp_backend

RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

EXPOSE $PORT

CMD uvicorn main:app --host 0.0.0.0 --port $PORT --reload