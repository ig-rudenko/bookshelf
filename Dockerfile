FROM python:3.12.2

WORKDIR /app

RUN pip install --upgrade --no-cache-dir pip && pip install poetry pymupdf --no-cache-dir;

COPY pyproject.toml poetry.lock /app/

RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi --no-cache;

COPY . .
RUN chmod +x run.sh
