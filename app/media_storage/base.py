from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import AsyncIterable, BinaryIO, Generator

from fastapi import UploadFile


class AbstractStorage(ABC):

    class FileNotFoundError(Exception):
        pass

    @abstractmethod
    async def upload_book(self, file: UploadFile, book_id: int) -> str:
        pass

    @abstractmethod
    def get_book_iterator(self, book_id: int) -> AsyncIterable[bytes]:
        pass

    @contextmanager
    @abstractmethod
    def get_book_binary(self, book_id: int) -> Generator[BinaryIO, None, None]:
        pass

    @abstractmethod
    async def upload_file(self, file_name: str, data: bytes) -> str:
        pass

    @contextmanager
    @abstractmethod
    def get_file_binary(self, file_name: str) -> Generator[BinaryIO, None, None]:
        pass

    @abstractmethod
    async def delete_book(self, book_id: int) -> None:
        pass
