from .base import AbstractStorage
from .local import LocalStorage
from .yandex import YandexStorage
from ..settings import settings


def get_storage() -> AbstractStorage:
    if settings.media_storage_type == "local":
        return LocalStorage(settings.media_root)
    elif settings.media_storage_type == "yadisk":
        return YandexStorage(settings.ya_disk_token)
