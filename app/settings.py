import logging
import sys
from pathlib import Path

from pydantic_settings import BaseSettings

logging.basicConfig(
    format="{levelname:<9} {module:<10} {funcName} -> {message}",
    style="{",
    handlers=[logging.StreamHandler(stream=sys.stdout)],
    level=logging.INFO,
)


class _BaseSettings(BaseSettings):
    logger: logging.Logger = logging.getLogger()
    log_level: str = "INFO"

    # Путь к медиа хранилищу
    media_storage_type: str = "local"
    media_storage: str = "./media"
    media_root: Path = Path(media_storage)
    media_root.mkdir(exist_ok=True, parents=True)

    database_url: str = ""  # Путь к базе данных
    media_url: str = "/media"

    REDIS_HOST: str = ""
    REDIS_PASSWORD: str | None = None
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    CELERY_BROKER_URL: str = ""  # Брокер сообщений для Celery


settings: _BaseSettings = _BaseSettings()
settings.logger.setLevel(settings.log_level)
