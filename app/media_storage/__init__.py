from .base import AbstractStorage
from .local import LocalStorage
from .s3 import S3Storage
from ..settings import settings, MediaStorageEnum


def get_storage() -> AbstractStorage:
    if settings.media_storage_type == MediaStorageEnum.s3:
        return S3Storage(bucket_name=settings.BUCKET_NAME, endpoint_url=settings.S3_ENDPOINT_URL)
    return LocalStorage(settings.media_root)
