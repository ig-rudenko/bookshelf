import enum
from pathlib import Path

from pydantic_settings import BaseSettings


class MediaStorageEnum(str, enum.Enum):
    local = "local"
    s3 = "s3"


class _BaseSettings(BaseSettings):
    log_level: str = "INFO"

    # Путь к медиа хранилищу
    media_storage_type: MediaStorageEnum = "local"
    media_storage: str = "./media"
    media_root: Path = Path(media_storage)
    media_root.mkdir(exist_ok=True, parents=True)

    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    BUCKET_NAME: str = ""
    AWS_REGION: str = ""
    S3_ENDPOINT_URL: str = ""

    database_url: str = ""  # Путь к базе данных
    media_url: str = "/media"

    REDIS_HOST: str = ""
    REDIS_PASSWORD: str | None = None
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    CELERY_BROKER_URL: str = ""  # Брокер сообщений для Celery

    # Google Captcha
    RECAPTCHA_ENABLED: bool = False
    RECAPTCHA_SITE_KEY: str = ""
    RECAPTCHA_SECRET_KEY: str = ""

    # Email
    EMAIL_FROM: str = ""
    EMAIL_PASSWORD: str = ""
    FORGET_PASSWORD_LINK_EXPIRE_MINUTES: int = 10


settings: _BaseSettings = _BaseSettings()
