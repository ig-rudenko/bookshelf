from src.application.books.commands import (
    CreateBookCommand,
    DeleteBookCommand,
    UpdateBookCommand,
    UpdateFavoriteCommand,
    UpdateReadCommand,
    UploadBookFileCommand,
)
from src.application.books.dto import (
    BookDTO,
    BookshelfLinkDTO,
    BookWithReadPagesDTO,
    DetailBookDTO,
    PublisherDTO,
    TagDTO,
)
from src.application.books.services import RecentBookService
from src.application.services.storage import AbstractStorage
from src.application.services.task_manager import TaskManager
from src.domain.books.entities import Book, BookFilter, BookmarksQueryFilter
from src.domain.bookshelves.entities import BookshelfFilter
from src.domain.common.exceptions import ObjectNotFoundError, PermissionDeniedError
from src.domain.common.unit_of_work import UnitOfWork
from src.domain.history.entities import BookReadHistoryFilter


class BookCommandHandler:
    def __init__(
        self,
        uow: UnitOfWork,
        storage: AbstractStorage,
        task_manager: TaskManager,
        recent_book_service: RecentBookService,
    ) -> None:
        self.uow = uow
        self.storage = storage
        self.task_manager = task_manager
        self.recent_book_service = recent_book_service

    async def handle_create(self, cmd: CreateBookCommand) -> BookDTO:
        if not cmd.user.is_staff:
            raise PermissionDeniedError("Недостаточно прав для создания книги")
        async with self.uow:
            book = await self.uow.books.add(
                Book.create(
                    user_id=cmd.user.id,
                    publisher=cmd.publisher,
                    title=cmd.title,
                    preview_image="",
                    file="",
                    authors=cmd.authors,
                    description=cmd.description,
                    pages=1,
                    size=1,
                    year=cmd.year,
                    private=cmd.private,
                    language=cmd.language,
                    tags=cmd.tags,
                )
            )
        await self.recent_book_service.delete_recent_books_cache()
        return await self._get_dto(book)

    async def handler_upload_file(self, cmd: UploadBookFileCommand) -> BookDTO:
        async with self.uow:
            book = await self.uow.books.get_by_id(cmd.book_id)
            if not cmd.user.is_superuser and book.user_id != cmd.user.id:
                raise PermissionDeniedError("Недостаточно прав для изменения книги")
            book.size = cmd.file.size or 0
            book.file = (await self.storage.upload_book(cmd.file, cmd.book_id))[:512]
            await self.uow.books.update(book)
        await self.task_manager.run_task("create_book_preview_task", book.id)  # Отправляем задачу
        return await self._get_dto(book)

    async def handle_update(self, cmd: UpdateBookCommand) -> BookDTO:
        async with self.uow:
            book = await self.uow.books.get_by_id(cmd.book_id)
            if not cmd.user.is_superuser and book.user_id != cmd.user.id:
                raise PermissionDeniedError("Недостаточно прав для изменения книги")
            book.publisher.name = cmd.publisher
            book.title = cmd.title
            book.authors = cmd.authors
            book.description = cmd.description
            book.year = cmd.year
            book.language = cmd.language
            book.private = cmd.private
            book.tags = cmd.tags
            await self.uow.books.update(book)

        await self.recent_book_service.delete_recent_books_cache()
        return await self._get_dto(book)

    async def handle_delete(self, cmd: DeleteBookCommand) -> None:
        async with self.uow:
            book = await self.uow.books.get_by_id(cmd.book_id)
            if not cmd.user.is_superuser and book.user_id != cmd.user.id:
                raise PermissionDeniedError("Недостаточно прав для изменения книги")
            await self.uow.books.delete(cmd.book_id)
            await self.uow.book_read_history.delete_for_book(cmd.book_id)
        await self.storage.delete_book(cmd.book_id)
        await self.recent_book_service.delete_recent_books_cache()

    async def _get_dto(self, book: Book) -> BookDTO:
        dto = BookDTO.from_domain(book)
        dto.preview_image = await self.storage.get_media_url(dto.preview_image)
        return dto


class BookQueryHandler:

    def __init__(
        self, uow: UnitOfWork, storage: AbstractStorage, recent_book_service: RecentBookService
    ) -> None:
        self.uow = uow
        self.storage = storage
        self.recent_book_service = recent_book_service

    async def handle_get_book(self, book_id: int) -> BookDTO:
        async with self.uow:
            book = await self.uow.books.get_by_id(book_id)

        book_dto = BookDTO.from_domain(book)
        book_dto.preview_image = await self.storage.get_media_url(book_dto.preview_image)
        return book_dto

    async def handle_get_book_detail(self, book_id: int, viewer_id: int | None) -> DetailBookDTO:
        async with self.uow:
            book = await self.uow.books.get_by_id(book_id)
            if viewer_id is not None:
                is_read = await self.uow.books.is_read_by_user(book_id, viewer_id)
                is_favorite = await self.uow.books.is_favorite_by_user(book_id, viewer_id)
            else:
                is_read = False
                is_favorite = False

            book_tags = await self.uow.books.get_book_tags(book_id)
            bookshelves, _ = await self.uow.bookshelves.get_filtered(
                BookshelfFilter(book_id=book_id, page=1, page_size=10, viewer_id=viewer_id)
            )
        media_url = await self.storage.get_media_url(book.preview_image)

        return DetailBookDTO(
            id=book.id,
            title=book.title,
            user_id=book.user_id,
            preview_image=media_url,
            authors=book.authors,
            description=book.description,
            pages=book.pages,
            size=book.size,
            year=book.year,
            private=book.private,
            language=book.language,
            favorite=is_favorite,
            read=is_read,
            publisher=PublisherDTO(
                id=book.publisher.id,
                name=book.publisher.name,
            ),
            tags=[TagDTO(id=tag.id, name=tag.name) for tag in book_tags],
            bookshelves=[
                BookshelfLinkDTO(
                    id=bookshelf.id,
                    name=bookshelf.name,
                    private=bookshelf.private,
                )
                for bookshelf in bookshelves
            ],
        )

    async def handle_get_list_books(self, query: BookFilter) -> tuple[list[BookDTO], int]:
        books, count = await self.uow.books.get_filtered(query)
        books_dto = []
        for book in books:
            dto = BookDTO.from_domain(book)
            dto.preview_image = await self.storage.get_media_url(book.preview_image)
            books_dto.append(dto)
        return books_dto, count

    async def handle_get_recent_books(self, user_id: int | None = None) -> list[BookDTO]:
        """
        Возвращает последние книги в порядке добавления.
        """
        query = BookFilter(viewer_id=user_id, page=1, page_size=25, sorted_by=["-id"])
        cached_books = await self.recent_book_service.get_recent_books(query)
        if cached_books is None:
            async with self.uow:
                books, _ = await self.uow.books.get_filtered(query)
            cached_books = []
            for book in books:
                dto = BookDTO.from_domain(book)
                dto.preview_image = await self.storage.get_media_url(book.preview_image)
                cached_books.append(dto)

            await self.recent_book_service.set_recent_books(cached_books, query)

        return cached_books

    async def handle_get_publishers(self, search: str | None, user_id: int | None) -> list[str]:
        async with self.uow:
            publishers = await self.uow.books.get_publishers(search, user_id)
            return publishers

    async def handle_get_authors(self, search: str | None, user_id: int | None) -> list[str]:
        async with self.uow:
            authors = await self.uow.books.get_authors(search, user_id)
            return authors

    async def handler_get_last_viewed_books(
        self, user_id: int | None, page: int, page_size: int
    ) -> tuple[list[BookWithReadPagesDTO], int]:
        async with self.uow:
            last_viewed_books, count = await self.uow.book_read_history.get_filtered(
                BookReadHistoryFilter(user_id=user_id, page=page, page_size=page_size)
            )
            viewed_books_map = {book.book_id: book for book in last_viewed_books}
            books_data, count = await self.uow.books.get_filtered(
                BookFilter(ids_in=list(viewed_books_map.keys()), page=page, page_size=page_size)
            )
            results = []
            for book in books_data:
                if book.id not in viewed_books_map:
                    raise ObjectNotFoundError(f"Book with id {book.id} not found in viewed books map")
                dto = BookWithReadPagesDTO.from_domain(book)
                dto.preview_image = await self.storage.get_media_url(book.preview_image)
                if viewed_books_map.get(book.id) is not None:
                    dto.read_pages = viewed_books_map[book.id].history.files[-1].page
                dto.last_time_read = viewed_books_map[book.id].updated_at
                results.append(dto)

            results = sorted(results, key=lambda x: x.last_time_read or 0, reverse=True)
            return results, count


class BookmarksCommandHandler:

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def handle_update_book_favorite(self, cmd: UpdateFavoriteCommand) -> None:
        async with self.uow:
            await self.uow.books.update_favorite_status(
                user_id=cmd.user_id,
                book_id=cmd.book_id,
                favorite=cmd.favorite,
            )

    async def handle_update_book_read(self, cmd: UpdateReadCommand) -> None:
        async with self.uow:
            await self.uow.books.update_read_status(
                user_id=cmd.user_id,
                book_id=cmd.book_id,
                read=cmd.read,
            )


class BookmarksQueryHandler:

    def __init__(self, uow: UnitOfWork, storage: AbstractStorage) -> None:
        self.uow = uow
        self.storage = storage

    async def handle_get_favorite_books(self, query: BookmarksQueryFilter) -> tuple[list[BookDTO], int]:
        async with self.uow:
            books, count = await self.uow.books.get_favorite_books(query)
        results = []
        for book in books:
            dto = BookDTO.from_domain(book)
            dto.preview_image = await self.storage.get_media_url(book.preview_image)
            results.append(dto)
        return results, count

    async def handle_get_favorite_books_count(self, user_id: int) -> int:
        async with self.uow:
            count = await self.uow.books.get_favorite_books_count(user_id)
            return count

    async def handle_get_read_books(self, query: BookmarksQueryFilter) -> tuple[list[BookDTO], int]:
        async with self.uow:
            books, count = await self.uow.books.get_read_books(query)
        results = []
        for book in books:
            dto = BookDTO.from_domain(book)
            dto.preview_image = await self.storage.get_media_url(book.preview_image)
            results.append(dto)
        return results, count

    async def handle_get_read_books_count(self, user_id: int) -> int:
        async with self.uow:
            count = await self.uow.books.get_read_books_count(user_id)
            return count
