import asyncio
import threading

from celery import Celery

from app.media_storage import get_storage
from app.orm.session_manager import db_manager
from app.services.aaa.reset_password import send_reset_password_email
from app.services.books import create_book_preview_and_update_pages_count, delete_recent_books_cache
from app.services.thumbnail import create_thumbnails
from app.settings import settings

db_manager.init(settings.database_url)

celery = Celery(__name__)
if settings.CELERY_BROKER_URL:
    celery.conf.broker_url = settings.CELERY_BROKER_URL
    loop = asyncio.get_event_loop()
else:
    print("celery.conf.task_always_eager")
    celery.conf.task_always_eager = True


def perform_async_task(coro):
    if celery.conf.task_always_eager:
        l = asyncio.new_event_loop()
        asyncio.set_event_loop(l)
        result = l.run_until_complete(coro)
        l.close()
        return result
    else:
        task = loop.create_task(coro)
        loop.run_until_complete(task)


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

    thread = threading.Thread(target=perform_async_task, args=(async_task(),))
    thread.start()
    thread.join()


@celery.task(name="send_reset_password_email_task", ignore_result=True)
def send_reset_password_email_task(email: str):
    """Задача отправки ссылки для сброса пароля"""
    send_reset_password_email(email)
