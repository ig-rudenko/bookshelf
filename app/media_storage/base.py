from abc import ABC, abstractmethod
from typing import AsyncIterable, BinaryIO, Iterator

from fastapi import File


class AbstractStorage(ABC):

    class FileNotFoundError(Exception):
        pass

    @abstractmethod
    async def upload_book(self, file: File, book_id: int) -> str:
        pass

    @abstractmethod
    def get_book_iterator(self, book_id: int) -> AsyncIterable[bytes]:
        pass

    @abstractmethod
    def get_book_binary(self, book_id: int) -> Iterator[BinaryIO]:
        pass

    @abstractmethod
    async def upload_file(self, file_name: str, data: bytes) -> str:
        pass

    @abstractmethod
    def get_file_binary(self, file_name: str) -> Iterator[BinaryIO]:
        pass

    @abstractmethod
    async def delete_book(self, book_id: int) -> None:
        pass
