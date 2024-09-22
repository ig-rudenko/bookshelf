FROM python:3.12.6-alpine

ENV PYTHONUNBUFFERED=1

RUN addgroup -g 10001 usergroup \
    && adduser -D -h /app -u 10002 user usergroup \
    && chown -R user:usergroup /app;

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir fastapi uvicorn aiohttp

COPY --chown=user:usergroup app.py /app

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
