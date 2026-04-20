FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ADD . /app

WORKDIR /app

RUN chmod +x /app/infra/entrypoint_backend_prepare.sh \
    /app/infra/entrypoint_server.sh \
    /app/infra/entrypoint_worker.sh \
    /app/infra/entrypoint_ws.sh

RUN uv sync --frozen

ENV PATH="/app/.venv/bin:$PATH"
