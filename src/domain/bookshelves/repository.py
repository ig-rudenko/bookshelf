from abc import ABC, abstractmethod

from .entities import Bookshelf, BookshelfFilter


class BookshelfRepository(ABC):

    @abstractmethod
    async def get(self, bookshelf_id: int) -> Bookshelf: ...

    @abstractmethod
    async def get_filtered(self, filter_: BookshelfFilter) -> tuple[list[Bookshelf], int]: ...

    @abstractmethod
    async def add(self, bookshelf: Bookshelf) -> Bookshelf: ...

    @abstractmethod
    async def update(self, bookshelf: Bookshelf) -> Bookshelf: ...

    @abstractmethod
    async def delete(self, bookshelf_id: int) -> None: ...
