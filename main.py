import os

from fastapi import FastAPI

from app.database.connector import db_conn
from app.handlers.auth import router as auth_router

app = FastAPI()

app.include_router(auth_router, prefix="/api/v1")


@app.get("/ping")
async def status():
    return {"message": "pong"}


@app.on_event("startup")
async def startup():
    db_conn.initialize(os.environ["DATABASE_URL"])
