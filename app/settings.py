from pathlib import Path

from pydantic_settings import BaseSettings


class _BaseSettings(BaseSettings):
    # Путь к медиа хранилищу
    media_root: Path = Path(__file__).parent.parent / "media"
    media_root.mkdir(exist_ok=True, parents=True)

    # Путь к базе данных
    database_url: str = ""


settings = _BaseSettings()
