FROM python:3.14.6-slim

ENV PYTHONOPTIMIZE=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1
SHELL ["/bin/sh", "-exc"]

ARG user_id=1000
ARG group_id=1001

RUN addgroup --gid $group_id app \
    && adduser --disabled-password --home /app --uid $user_id --gid $group_id app \
    && chown -R $user_id:$group_id /app;

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir fastapi uvicorn aiohttp

COPY --chown=$user_id:$group_id app.py /app

EXPOSE 8000/tcp

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
