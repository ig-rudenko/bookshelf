import asyncio
import os

from celery import Celery

from app.orm.session_manager import db_manager
from app.services.books import create_book_preview, delete_recent_books_cache
from app.settings import settings

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
db_manager.init(settings.database_url)


@celery.task(name="create_book_preview", ignore_result=True)
def create_book_preview_task(book_id):
    async def async_task():
        await create_book_preview(book_id)
        # Удаляем кэш недавно добавленных книг, потому что могла замениться обложка книги
        await delete_recent_books_cache()

    print(asyncio.run(async_task()))
