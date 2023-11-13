FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip3 install --upgrade pip
RUN pip3 install poetry --no-cache-dir
RUN poetry config virtualenvs.create false && poetry install --no-root --no-directory --no-dev --no-interaction --no-ansi

COPY src/pet_alert ./

COPY entrypoint.sh ./

RUN chmod +x entrypoint.sh

ENTRYPOINT [ "/app/entrypoint.sh" ]