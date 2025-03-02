FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip3 install poetry --no-cache-dir
RUN poetry config virtualenvs.create false && poetry install --no-root --no-directory --no-interaction --no-ansi
# --without dev

COPY . .
