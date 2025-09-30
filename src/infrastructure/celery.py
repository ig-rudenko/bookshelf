import asyncio
import threading
from collections.abc import Callable

from celery import Celery, Task

from src.application.books.services import RecentBookService, create_book_preview_and_update_pages_count
from src.application.services.task_manager import TaskManager
from src.application.services.thumbnail import create_thumbnails
from src.infrastructure.cache import RedisCache
from src.infrastructure.db.repositories.books_repo import SqlAlchemyBookRepository
from src.infrastructure.db.session_manager import db_manager, scoped_session
from src.infrastructure.dependencies import get_storage
from src.infrastructure.email import SMTPEmailService
from src.infrastructure.settings import settings

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
        loop_ = asyncio.new_event_loop()
        asyncio.set_event_loop(loop_)
        result = loop_.run_until_complete(coro)
        loop_.close()
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
        cache = RedisCache(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            max_connections=1,
        )
        recent_book_service = RecentBookService(cache)
        storage = get_storage()

        # noinspection PyArgumentList
        async with scoped_session() as session:
            repo = SqlAlchemyBookRepository(session)
            preview_name = await create_book_preview_and_update_pages_count(storage, repo, book_id)

        # Создаем эскизы обложки.
        await create_thumbnails(storage, preview_name)

        # Удаляем кэш недавно добавленных книг
        await recent_book_service.delete_recent_books_cache()

    thread = threading.Thread(target=perform_async_task, args=(async_task(),))
    thread.start()
    thread.join()


@celery.task(name="send_reset_password_email_task", ignore_result=True)
def send_reset_password_email_task(email: str):
    """Задача отправки ссылки для сброса пароля"""
    email_service = SMTPEmailService(
        settings.EMAIL_FROM, settings.EMAIL_PASSWORD, settings.SMTP_SERVER, settings.SMTP_PORT
    )
    email_service.send_reset_password_email(email)


class CeleryTaskManager(TaskManager):
    def __init__(self, celery_app: Celery):
        self.celery_app: Celery = celery_app

    async def register_task(self, name: str, task: Callable):
        if name not in self.celery_app.tasks:
            self.celery_app.task(task)

    async def run_task(self, name: str, *args, **kwargs) -> str:
        if name in self.celery_app.tasks:
            task: Task = self.celery_app.tasks[name]
            return task.delay(*args, **kwargs).task_id
        raise TaskManager.TaskNotFound(f"Task `{name}` not found")


celery.task()
celery_task_manager = CeleryTaskManager(celery)
celery_task_manager.register_task(
    "create_book_preview_task",
    lambda book_id: create_book_preview_task.delay(book_id),
)
celery_task_manager.register_task(
    "send_reset_password_email_task",
    lambda email: send_reset_password_email_task.delay(email),
)
