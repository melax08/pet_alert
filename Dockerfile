FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip3 install --upgrade pip
RUN pip3 install poetry --no-cache-dir
RUN poetry config virtualenvs.create false && poetry install --no-root --no-directory --no-dev --no-interaction --no-ansi

COPY src/pet_alert ./

COPY entrypoint_server.sh entrypoint_worker.sh .env ./

RUN chmod +x entrypoint_server.sh
RUN chmod +x entrypoint_worker.sh
