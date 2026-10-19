FROM python:3.14.8-slim AS builder

ARG python_version=3.14

SHELL ["/bin/sh", "-exc"]

COPY --from=ghcr.io/astral-sh/uv:0.13.1 /uv /uvx /bin/

WORKDIR /app

ENV UV_PYTHON="python$python_version" \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/app/venv \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    PYTHONOPTIMIZE=1

COPY pyproject.toml uv.lock /app/

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync \
      --no-dev \
      --no-install-project \
      --frozen


FROM python:3.14.8-slim

ARG user_id=1000
ARG group_id=1000

WORKDIR /app

SHELL ["/bin/sh", "-exc"]

RUN addgroup --gid $group_id app \
    && adduser --disabled-password --home /app --uid $user_id --gid $group_id app \
    && chown -R $user_id:$group_id /app;

ENV PATH=/app/venv/bin:$PATH \
    PYTHONOPTIMIZE=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1

COPY --chown=$user_id:$group_id . /app
COPY --link --from=builder /app/venv/ /app/venv

RUN chmod +x run.sh

USER $user_id:$group_id
EXPOSE 8000/tcp
STOPSIGNAL SIGINT

CMD ["/bin/bash", "/app/run.sh"]
