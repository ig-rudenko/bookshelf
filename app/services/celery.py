import asyncio
from threading import Thread

from celery import Celery

from app.media_storage import get_storage
from app.orm.session_manager import db_manager
from app.services.books import create_book_preview_and_update_pages_count, delete_recent_books_cache
from app.services.thumbnail import create_thumbnails
from app.settings import settings

celery = Celery(__name__)
if settings.CELERY_BROKER_URL:
    celery.conf.broker_url = settings.CELERY_BROKER_URL
else:
    celery.conf.task_always_eager = True
db_manager.init(settings.database_url)


@celery.task(name="create_book_preview", ignore_result=True)
def create_book_preview_task(book_id: int):
    """
    Задача создания обложки книги.
    """

    async def async_task():
        storage = get_storage()
        preview_name = await create_book_preview_and_update_pages_count(storage, book_id)

        # Создаем эскизы обложки.
        await create_thumbnails(storage, preview_name)

        # Удаляем кэш недавно добавленных книг
        await delete_recent_books_cache()

    def sync_task():
        loop = asyncio.new_event_loop()
        loop.run_until_complete(async_task())

    try:
        sync_task()
    except RuntimeError:
        thread = Thread(target=sync_task)
        thread.start()
        thread.join()
