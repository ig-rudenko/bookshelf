FROM python:3.13.9-alpine

ENV PYTHONOPTIMIZE=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1
SHELL ["/bin/sh", "-exc"]

ARG user_id=1000
ARG group_id=1001

RUN addgroup -g $group_id usergroup \
    && adduser -D -h /app -u $user_id user $group_id \
    && chown -R $user_id:$group_id /app;

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir fastapi uvicorn aiohttp

COPY --chown=$user_id:$group_id app.py /app

EXPOSE 8000/tcp

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
