from typing import BinaryIO

# noinspection PyPackageRequirements
import fitz

from src.domain.books.entities import BookFilter
from src.domain.books.repository import BookRepository
from .dto import BookDTO
from ..services.cache import AbstractCache
from ..services.storage import AbstractStorage


class RecentBookService:
    base_cache_key = "recent_books"

    def __init__(self, cache: AbstractCache, cache_ttl: int = 60 * 60 * 24):
        self.cache = cache
        self.cache_ttl = cache_ttl

    async def _get_cache_key(self, query: BookFilter) -> str:
        return f"{self.base_cache_key}:viewer:{query.viewer_id}:page_size:{query.page_size}"

    async def get_recent_books(self, query: BookFilter) -> list[BookDTO] | None:
        cache_key = await self._get_cache_key(query)
        return await self.cache.get(cache_key)

    async def set_recent_books(self, books: list[BookDTO], query: BookFilter) -> None:
        if books:
            cache_key = await self._get_cache_key(query)
            await self.cache.set(cache_key, books, self.cache_ttl)

    async def delete_recent_books_cache(self) -> None:
        await self.cache.delete_namespace(self.base_cache_key)


async def create_book_preview_and_update_pages_count(
    storage: AbstractStorage, book_repository: BookRepository, book_id: int
) -> str:
    """
    Создает превью книги из первой страницы PDF документа и обновляет ее количество страниц в БД.

    :param storage: :class:`AbstractStorage` объект хранилища.
    :param book_repository: :class:`BookRepository` объект репозитория книг.
    :param book_id: Идентификатор книги.

    :return: Ссылка на превью книги.
    """
    with storage.get_book_binary(book_id) as file_data:  # type: BinaryIO
        doc = fitz.Document(stream=file_data.read())

    total_pages: int = doc.page_count
    page = doc.load_page(0)
    pix: fitz.Pixmap = page.get_pixmap()
    image: bytearray = pix.tobytes()

    preview_name = f"previews/{book_id}/preview.png"
    await storage.upload_file(preview_name, image)

    book = await book_repository.get_by_id(book_id)
    book.preview_image = preview_name
    book.pages = total_pages
    await book_repository.update(book)
    return preview_name
