FROM python:3.12.6-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN curl -sSL https://install.python-poetry.org | python -

# Добавляем Poetry в PATH
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

RUN pip install --upgrade --no-cache-dir pip && pip install pymupdf --no-cache-dir;

COPY pyproject.toml poetry.lock /app/

RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi --no-cache;


FROM python:3.12.6-slim

ENV PYTHONUNBUFFERED=1

RUN addgroup --gid 10001 app \
    && adduser --disabled-password --home /app --uid 10001 --gid 10001 app \
    && chown -R app:app /app;

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем зависимости из builder-этапа
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY --chown=app:app . /app

RUN chmod +x run.sh

USER app

EXPOSE 8000

CMD ["/bin/bash", "/app/run.sh"]
