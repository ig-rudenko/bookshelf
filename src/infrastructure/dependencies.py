from src.application.services.cache import AbstractCache
from src.application.services.storage import AbstractStorage
from src.application.services.task_manager import TaskManager

from .cache import InMemoryCache, RedisCache
from .media_storage import LocalStorage, S3Storage
from .settings import MediaStorageEnum, settings

__cache__: AbstractCache | None = None
__storage__: AbstractStorage | None = None
__task_manager__: TaskManager | None = None


def get_cache() -> AbstractCache:
    """Возвращает кэш в зависимости от настроек приложения"""

    global __cache__
    if __cache__ is None:
        if settings.REDIS_HOST:
            __cache__ = RedisCache(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
            )
        else:
            __cache__ = InMemoryCache()
    return __cache__


def get_storage() -> AbstractStorage:
    global __storage__
    if __storage__ is None:
        if settings.media_storage_type == MediaStorageEnum.s3:
            __storage__ = S3Storage(bucket_name=settings.BUCKET_NAME, endpoint_url=settings.S3_ENDPOINT_URL)
        else:
            __storage__ = LocalStorage(settings.media_root)
    return __storage__


def get_task_manager() -> TaskManager:
    global __task_manager__
    from .celery import celery_task_manager

    if __task_manager__ is None:
        __task_manager__ = celery_task_manager
    return __task_manager__
