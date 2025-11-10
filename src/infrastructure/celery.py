import asyncio
from collections.abc import Callable
from functools import wraps

import loguru
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

if db_manager.session_maker is None:
    db_manager.init(
        settings.database_url,
        echo=settings.database_echo,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
    )

celery = Celery(__name__)
if settings.CELERY_BROKER_URL:
    celery.conf.broker_url = settings.CELERY_BROKER_URL
else:
    loguru.logger.warning("⚠️ celery.conf.task_always_eager = True")
    celery.conf.task_always_eager = True


def celery_async_task(*celery_args, **celery_kwargs):
    """
    Декоратор для создания async Celery-задач.
    Работает корректно и при task_always_eager=True.
    """

    def decorator(func):
        # обычная celery-задача (но func — async)
        task = celery.task(*celery_args, **celery_kwargs)(_wrap_async(func))
        return task

    return decorator


def _wrap_async(async_func):
    """Обёртка, которая выполняет async функцию в подходящем event loop."""

    @wraps(async_func)
    def wrapper(*args, **kwargs):
        coro = async_func(*args, **kwargs)
        try:
            loop = asyncio.get_running_loop()
        except Exception:
            # Нет активного event loop (например, worker) → создаём новый
            return asyncio.run(coro)
        else:
            # Есть активный loop (например, FastAPI + task_always_eager=True)
            return loop.create_task(coro)

    return wrapper


@celery_async_task(name="create_book_preview_task", ignore_result=True)
async def create_book_preview_task(book_id: int):
    """
    Асинхронная логика задачи (используется SQLAlchemy, Redis и другие async-компоненты)
    """
    cache = RedisCache(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD,
        max_connections=1,
    )
    recent_book_service = RecentBookService(cache)
    storage = get_storage()

    # Работа с базой
    async with scoped_session() as session:
        repo = SqlAlchemyBookRepository(session)
        preview_name = await create_book_preview_and_update_pages_count(storage, repo, book_id)

    # Создание миниатюр
    await create_thumbnails(storage, preview_name)

    # Очистка кэша
    await recent_book_service.delete_recent_books_cache()


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


async def register_tasks():
    await celery_task_manager.register_task(
        "create_book_preview_task",
        lambda book_id: create_book_preview_task.delay(book_id),
    )
    await celery_task_manager.register_task(
        "send_reset_password_email_task",
        lambda email: send_reset_password_email_task.delay(email),
    )
