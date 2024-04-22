import asyncio
import os

from celery import Celery

from app.orm.session_manager import db_manager
from app.services.books import create_book_preview
from app.settings import settings

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
db_manager.init(settings.database_url)


@celery.task(name="create_book_preview", ignore_result=True)
def create_book_preview_task(book_id):
    loop = asyncio.get_event_loop()
    print(loop.run_until_complete(create_book_preview(book_id)))
