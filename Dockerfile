# syntax=docker/dockerfile:1.3-labs
FROM python:3.12-bookworm

WORKDIR /app/

RUN pip install --upgrade pip poetry

COPY pyproject.toml poetry.lock /app/

RUN poetry config virtualenvs.create false && poetry install --no-interaction

COPY django_webhook /app/django_webhook
COPY tests /app/tests
COPY manage.py /app/manage.py

CMD /app/manage.py runserver_plus 0.0.0.0:8000
