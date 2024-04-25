from .base import AbstractStorage
from .local import LocalStorage
from ..settings import settings


def get_storage() -> AbstractStorage:
    return LocalStorage(settings.media_root)
