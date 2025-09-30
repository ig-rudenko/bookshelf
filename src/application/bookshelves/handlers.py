from src.application.bookshelves.commands import (
    BookshelfCreateCommand,
    BookshelfDeleteCommand,
    BookshelfUpdateCommand,
)
from src.application.bookshelves.dto import BookshelfDTO
from src.domain.bookshelves.entities import Bookshelf, BookshelfFilter
from src.domain.common.exceptions import ObjectNotFoundError
from src.domain.common.unit_of_work import UnitOfWork


class BookshelfQueryHandler:

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def handle_filter(self, filter_: BookshelfFilter) -> tuple[list[BookshelfDTO], int]:
        async with self.uow:
            bookshelves, count = await self.uow.bookshelves.get_filtered(filter_)
            return [BookshelfDTO.from_domain(obj) for obj in bookshelves], count

    async def handle_get(self, id_: int, user_id: int | None) -> BookshelfDTO:
        async with self.uow:
            bookshelf = await self.uow.bookshelves.get(id_)
            if bookshelf.private and bookshelf.user_id != user_id:
                raise ObjectNotFoundError("Object not found")
            return BookshelfDTO.from_domain(bookshelf)


class BookshelfCommandHandler:

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def handle_create(self, cmd: BookshelfCreateCommand) -> BookshelfDTO:
        if not cmd.user.is_superuser:
            # Если пользователь не является суперпользователем, то книжная полка может быть только приватной
            cmd.private = True

        async with self.uow:
            bookshelf = await self.uow.bookshelves.add(
                Bookshelf.create(
                    name=cmd.name,
                    description=cmd.description,
                    user_id=cmd.user.id,
                    private=cmd.private,
                    books=cmd.books,
                )
            )
            return BookshelfDTO.from_domain(bookshelf)

    async def handle_update(self, cmd: BookshelfUpdateCommand) -> BookshelfDTO:
        if not cmd.user.is_superuser:
            # Если пользователь не является суперпользователем, то книжная полка может быть только приватной
            cmd.private = True

        async with self.uow:
            bookshelf = await self.uow.bookshelves.get(cmd.id)
            bookshelf.private = cmd.private
            bookshelf.name = cmd.name
            bookshelf.description = cmd.description
            bookshelf.set_books(cmd.books)
            bookshelf = await self.uow.bookshelves.update(bookshelf)
            return BookshelfDTO.from_domain(bookshelf)

    async def handle_delete(self, cmd: BookshelfDeleteCommand) -> None:
        async with self.uow:
            bookshelf = await self.uow.bookshelves.get(cmd.id)
            if bookshelf.user_id != cmd.user.id and not cmd.user.is_superuser:
                raise ObjectNotFoundError("Object not found")
            await self.uow.bookshelves.delete(cmd.id)
