from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import AsyncIterable, BinaryIO, Generator

from fastapi import UploadFile


class AbstractStorage(ABC):
    """Абстрактное хранилище для книг."""

    class FileNotFoundError(Exception):
        """Класс ошибки файла не найдено."""

        pass

    @abstractmethod
    async def upload_book(self, file: UploadFile, book_id: int) -> str:
        """
        Загружает файл книги в хранилище.
        Удаляет старые файлы книги перед загрузкой новой.

        :param file: Файл книги.
        :param book_id: Идентификатор книги.
        :return: Путь к загруженной книге в хранилище.
        """
        pass

    @abstractmethod
    def get_book_iterator(self, book_id: int) -> AsyncIterable[bytes]:
        """
        Возвращает асинхронный итератор по байтам книги.
        :param book_id: Идентификатор книги.
        :return: Итератор по байтам книги.
        :raises self.FileNotFoundError:  :class:`AbstractStorage.FileNotFoundError` Если книга не найдена.
        """
        pass

    @contextmanager
    @abstractmethod
    def get_book_binary(self, book_id: int) -> Generator[BinaryIO, None, None]:
        """
        Возвращает итератор бинарного файла книги.
        :param book_id: Идентификатор книги.
        :return: Бинарный файл книги.
        :raises self.FileNotFoundError:  :class:`AbstractStorage.FileNotFoundError` Если книга не найдена.
        """
        pass

    @abstractmethod
    async def upload_file(self, file_name: str, data: bytes) -> str:
        """
        Загружает файл в хранилище.
        :param file_name: Имя файла.
        :param data: Данные файла.
        :return: Путь к загруженному файлу.
        """
        pass

    @contextmanager
    @abstractmethod
    def get_file_binary(self, file_name: str) -> Generator[BinaryIO, None, None]:
        """
        Возвращает итератор бинарного файла.
        :param file_name: Путь к файлу в хранилище.
        :return: Бинарный файл.
        :raises self.FileNotFoundError:  :class:`AbstractStorage.FileNotFoundError` Если файл не найден.
        """
        pass

    @abstractmethod
    async def delete_book(self, book_id: int) -> None:
        """
        Удаляет книгу из хранилища и все её превью с эскизами.
        :param book_id: Идентификатор книги.
        """
        pass
