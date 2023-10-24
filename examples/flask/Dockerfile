# syntax=docker/dockerfile:1.3-labs
FROM python:3.12-bookworm

WORKDIR /app/

RUN pip install --upgrade pip flask

COPY server.py /app/server.py

CMD flask --app server.py --debug run --host 0.0.0.0 --port 8002
