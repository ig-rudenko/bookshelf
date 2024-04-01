import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database.connector import db_conn
from app.handlers.auth import router as auth_router
from app.handlers.books import router as book_router


@asynccontextmanager
async def startup(app_instance: FastAPI):
    db_conn.initialize(os.environ["DATABASE_URL"])
    print("Database initialized")
    yield
    print("Database closed")
    db_conn.session.close_all()


app = FastAPI(lifespan=startup)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(book_router, prefix="/api/v1")


@app.get("/ping", tags=["health"])
async def status():
    return {"message": "pong"}
