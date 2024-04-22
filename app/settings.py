from pathlib import Path

from pydantic_settings import BaseSettings


class _BaseSettings(BaseSettings):
    # Путь к медиа хранилищу
    media_storage: str = "./media"
    media_root: Path = Path(media_storage)
    media_root.mkdir(exist_ok=True, parents=True)

    # Путь к базе данных
    database_url: str = ""
    media_url: str = "/media"


settings = _BaseSettings()
