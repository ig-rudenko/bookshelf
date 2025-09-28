import re
import shutil
from contextlib import contextmanager
from pathlib import Path
from typing import AsyncIterable, BinaryIO, Iterator

import aiofiles
from slugify import slugify

from src.application.services.storage import AbstractStorage, FileProtocol
from src.infrastructure.settings import settings


class LocalStorage(AbstractStorage):
    """Локальное хранилище для книг. В файловой системе."""

    def __init__(self, media_root: str | Path):
        self._media_root = self._format_media_root(media_root)

    @staticmethod
    def _format_media_root(media_root: str | Path) -> Path:
        if isinstance(media_root, str):
            return Path(media_root)
        return media_root

    @property
    def media_root(self):
        return self._media_root

    @media_root.setter
    def media_root(self, value):
        self._media_root = self._format_media_root(value)

    async def upload_book(self, file: FileProtocol, book_id: int) -> str:
        """
        Загружает файл книги в хранилище.
        Удаляет старые файлы книги перед загрузкой новой.

        :param file: Файл книги.
        :param book_id: Идентификатор книги.
        :return: Путь к загруженной книге в хранилище.
        """
        # Фильтруем запрещенные символы
        if file_match := re.search(r"(?P<file_name>.+)\.pdf$", str(file.filename)):
            file_name = file_match.group("file_name")
        else:
            file_name = f"book_{book_id}"

        file_name = slugify(file_name) + ".pdf"
        # Создаем директорию для хранения книги
        book_folder = self._media_root / "books" / str(book_id)
        book_folder.mkdir(parents=True, exist_ok=True)
        book_file_path = book_folder / file_name

        # Удаляем старый файл книги
        for old_file in book_folder.glob("*.pdf"):
            old_file.unlink()

        async with aiofiles.open(book_file_path, "wb") as f:
            while content := await file.read(1024 * 1024):
                await f.write(content)

        return f"books/{book_id}/{file_name}"

    async def get_book_iterator(self, book_id: int) -> AsyncIterable[bytes]:
        """
        Возвращает асинхронный итератор по байтам книги.
        :param book_id: Идентификатор книги.
        :return: Итератор по байтам книги.
        :raises self.FileNotFoundError:  :class:`AbstractStorage.FileNotFoundError` Если книга не найдена.
        """

        # Директория хранения книги.
        book_folder = self._media_root / "books" / str(book_id)
        # Ищем файл книги.
        file_name = ""
        for file in book_folder.glob("*"):
            file_name = file.name
        if not file_name:
            raise self.FileNotFoundError

        try:
            async with aiofiles.open(book_folder / file_name, "rb") as f:
                while content := await f.read(1024 * 1024):
                    yield content
        except OSError:
            raise self.FileNotFoundError

    @contextmanager
    def get_book_binary(self, book_id: int) -> Iterator[BinaryIO]:
        """
        Возвращает итератор бинарного файла книги.
        :param book_id: Идентификатор книги.
        :return: Бинарный файл книги.
        :raises self.FileNotFoundError:  :class:`AbstractStorage.FileNotFoundError` Если книга не найдена.
        """

        # Директория хранения книги.
        book_folder = self._media_root / "books" / str(book_id)
        # Ищем файл книги.
        file_name = ""
        for file in book_folder.glob("*"):
            file_name = file.name
        if not file_name:
            raise self.FileNotFoundError

        try:
            book_file = open(book_folder / file_name, "rb")
        except OSError:
            raise self.FileNotFoundError
        try:
            yield book_file
        finally:
            book_file.close()

    async def upload_file(self, file_name: str, data: bytes) -> str:
        """
        Загружает файл в хранилище.
        :param file_name: Имя файла.
        :param data: Данные файла.
        :return: Путь к загруженному файлу.
        """

        file_path = self._media_root / file_name
        file_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(data)
        return file_name

    @contextmanager
    def get_file_binary(self, file_name: str) -> Iterator[BinaryIO]:
        """
        Возвращает итератор бинарного файла.
        :param file_name: Путь к файлу в хранилище.
        :return: Бинарный файл.
        :raises self.FileNotFoundError:  :class:`AbstractStorage.FileNotFoundError` Если файл не найден.
        """
        try:
            file = open(self._media_root / file_name, "rb")
        except OSError:
            raise self.FileNotFoundError
        try:
            yield file
        finally:
            file.close()

    async def delete_book(self, book_id: int) -> None:
        """
        Удаляет книгу из хранилища и все её превью с эскизами.
        :param book_id: Идентификатор книги.
        """
        try:
            shutil.rmtree(self._media_root / "books" / str(book_id))
            shutil.rmtree(self._media_root / "previews" / str(book_id))
        except FileNotFoundError:
            pass

    async def get_media_url(self, file: str) -> str:
        if file.startswith("/media"):
            file = file[6:]
        elif file.startswith("media"):
            file = file[5:]
        if not file.startswith("/"):
            file = "/" + file

        if not settings.media_url.startswith("http") and not settings.media_url.startswith("/"):
            settings.media_url = "/" + settings.media_url

        if settings.media_url.endswith("/"):
            return settings.media_url[:-1] + file

        return settings.media_url + file
