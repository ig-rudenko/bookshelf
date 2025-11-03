import enum
from pathlib import Path
from uuid import uuid4

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MediaStorageEnum(str, enum.Enum):
    local = "local"
    s3 = "s3"


class _BaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.example", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    log_level: str = "INFO"

    jwt_secret: str = Field(default_factory=lambda: str(uuid4()))
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 30

    # Путь к медиа хранилищу
    media_storage_type: MediaStorageEnum = MediaStorageEnum.local
    media_storage: str = "./media"
    media_root: Path = Path(media_storage)
    media_root.mkdir(exist_ok=True, parents=True)

    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    BUCKET_NAME: str = ""
    AWS_REGION: str = ""
    S3_ENDPOINT_URL: str = ""

    database_url: str = ""  # Путь к базе данных
    database_echo: bool = False
    database_pool_size: int = 10
    database_max_overflow: int = 20
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
    SMTP_SERVER: str = "smtp.yandex.ru"
    SMTP_PORT: int = 465
    FORGET_PASSWORD_LINK_EXPIRE_MINUTES: int = 10


settings: _BaseSettings = _BaseSettings()
