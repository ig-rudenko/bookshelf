from src.application.books.commands import CreateBookCommand, UpdateBookCommand
from src.application.books.dto import BookDTO, DetailBookDTO, TagDTO, BookshelfLinkDTO
from src.application.books.services import RecentBookService
from src.application.services.storage import AbstractStorage, FileProtocol
from src.application.services.task_manager import TaskManager
from src.domain.books.entities import Book, BookFilter
from src.domain.bookshelves.entities import BookshelfFilter
from src.domain.common.unit_of_work import UnitOfWork


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
        async with self.uow:
            book = await self.uow.books.add(
                Book.create(
                    user_id=cmd.user_id,
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
        return BookDTO.from_domain(book)

    async def handler_upload_file(self, book_id: int, file: FileProtocol) -> None:
        async with self.uow:
            book = await self.uow.books.get_by_id(book_id)
            book.size = file.size
            await self.uow.books.update(book)
            await self.storage.upload_book(file, book_id)
        await self.task_manager.run_task("create_book_preview_task", book.id)  # Отправляем задачу

    async def handle_update(self, cmd: UpdateBookCommand) -> BookDTO:
        async with self.uow:
            book = await self.uow.books.get_by_id(cmd.book_id)
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
        return BookDTO.from_domain(book)

    async def handle_delete(self, book_id: int) -> None:
        async with self.uow:
            await self.uow.books.delete(book_id)
            await self.uow.book_read_history.delete(book_id)
        await self.storage.delete_book(book_id)
        await self.recent_book_service.delete_recent_books_cache()


class BookQueryHandler:

    def __init__(
        self, uow: UnitOfWork, storage: AbstractStorage, recent_book_service: RecentBookService
    ) -> None:
        self.uow = uow
        self.storage = storage
        self.recent_book_service = recent_book_service

    async def handle_get_book_detail(self, book_id: int, user_id: int) -> DetailBookDTO:
        async with self.uow:
            book = await self.uow.books.get_by_id(book_id)
            is_read = await self.uow.books.is_read_by_user(user_id)
            is_favorite = await self.uow.books.is_favorite_by_user(user_id)
            book_tags = await self.uow.books.get_book_tags(book_id)
            bookshelves, _ = await self.uow.bookshelves.get_filtered(
                BookshelfFilter(book_id=book_id, page=1, page_size=10)
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
            publisher=book.publisher.name,
            publisher_id=book.publisher.id,
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
        return [BookDTO.from_domain(book) for book in books], count

    async def handle_get_recent_books(self, user_id: int) -> list[BookDTO]:
        """
        Возвращает последние книги в порядке добавления.
        """
        query = BookFilter(viewer_id=user_id, page=1, page_size=25, sorted_by=["-id"])
        cached_books = await self.recent_book_service.get_recent_books(query)
        if cached_books is None:
            async with self.uow:
                books, count = await self.uow.books.get_filtered(query)
            cached_books = [BookDTO.from_domain(book) for book in books]
            await self.recent_book_service.set_recent_books(cached_books, query)

        return cached_books
