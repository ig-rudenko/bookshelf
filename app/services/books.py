import re
import shutil
from typing import TypeVar, TypedDict

import aiofiles
import fitz
from fastapi import UploadFile
from slugify import slugify
from sqlalchemy import select, func, Select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import query_count
from app.crud.books import get_book
from app.models import Book, User, Tag, Publisher
from app.orm.session_manager import db_manager
from app.schemas.books import BookSchema, BooksSchemaPaginated
from app.services.cache import get_cache, cached
from app.services.paginator import paginate
from app.services.thumbnail import create_thumbnails, get_thumbnail
from app.settings import settings


async def get_paginated_books(session: AsyncSession, query, paginator) -> BooksSchemaPaginated:
    query = paginate(query, page=paginator["page"], per_page=paginator["per_page"])

    res = await session.execute(query)
    res.unique()
    count = await query_count(query, session)
    books = [BookSchema.model_validate(row) for row in res.scalars()]

    # Заменяем оригинальные картинки на миниатюры
    for book in books:
        book.preview_image = get_thumbnail(book.preview_image, "medium")

    return BooksSchemaPaginated(
        books=books,
        total_count=count,
        current_page=paginator["page"],
        max_pages=count // paginator["per_page"] or 1,
        per_page=paginator["per_page"],
    )


class QueryParams(TypedDict):
    search: str | None
    title: str | None
    authors: str | None
    publisher: str | None
    year: int | None
    language: str | None
    pages_gt: int | None
    pages_lt: int | None
    description: str | None
    only_private: bool | None
    tags: list[str] | None
    page: int
    per_page: int


async def get_filtered_books(
    session: AsyncSession,
    user: User | None,
    query_params: QueryParams,
) -> BooksSchemaPaginated:
    """Возвращает список книг и количество, которые являются публичными"""

    query = select(Book).order_by(Book.year.desc(), Book.id.desc()).group_by(Book.id)
    query = _filter_books_query_by_params(query, query_params)

    if user is not None:
        query = query.where(Book.private.is_(False) | (Book.private.is_(True) & (Book.user_id == user.id)))
    else:
        query = query.where(Book.private.is_(False))

    return await get_paginated_books(session, query, query_params)


async def set_file(session: AsyncSession, file: UploadFile, book: Book):
    """
    Создаем для книги файл, а также превью для его просмотра.
    """
    # Фильтруем запрещенные символы
    if file_match := re.search(r"(?P<file_name>.+)\.pdf$", str(file.filename)):
        file_name = file_match.group("file_name")
    else:
        file_name = f"book_{book.id}"

    file_name = slugify(file_name) + ".pdf"
    # Создаем директорию для хранения книги
    book_folder = settings.media_root / "books" / str(book.id)
    book_folder.mkdir(parents=True, exist_ok=True)
    book_file_path = book_folder / file_name

    # Удаляем старый файл книги
    for old_file in book_folder.glob("*.pdf"):
        old_file.unlink()

    async with aiofiles.open(book_file_path, "wb") as f:
        while content := await file.read(1024 * 1024):
            await f.write(content)

    book.file = f"books/{book.id}/{file_name}"
    book.size = book_file_path.stat().st_size
    await book.save(session)


async def create_book_preview(book_id: int) -> str:
    try:
        # Создаем директорию для хранения книги
        book_folder = settings.media_root / "books" / str(book_id)
        preview_folder = settings.media_root / "previews" / str(book_id)
        preview_folder.mkdir(parents=True, exist_ok=True)

        # Получаем расширение файла
        file_name = ""
        for file in book_folder.glob("*"):
            file_name = file.name
        if not file_name:
            return "Book file not found"

        book_file_path = book_folder / file_name
        book_preview_path = preview_folder / "preview.png"

        doc = fitz.Document(book_file_path.absolute())
        page = doc.load_page(0)
        pix = page.get_pixmap()
        pix.save(book_preview_path.absolute())

        async with db_manager.session() as session:
            book = await Book.get(session, id=book_id)
            book.preview_image = f"{settings.media_url}/previews/{book_id}/preview.png"
            book.pages = doc.page_count
            await book.save(session)

        create_thumbnails(book_preview_path)

        return "Done"

    except Exception as exc:
        return str(exc)


_QT = TypeVar("_QT", bound=Select)


def _filter_books_query_by_params(query: _QT, query_params: QueryParams) -> _QT:
    if query_params["search"]:
        query = query.where(
            Book.title.ilike(f'%{query_params["search"]}%')
            | Book.description.ilike(f'%{query_params["search"]}%')
        )
    if query_params["title"]:
        query = query.where(Book.title.ilike(f'%{query_params["title"]}%'))
    if query_params["authors"]:
        query = query.where(Book.authors.ilike(f'%{query_params["authors"]}%'))
    if query_params["publisher"]:
        query = query.join(Book.publisher).filter(Publisher.name.ilike(f'%{query_params["publisher"]}%'))
    if query_params["year"]:
        query = query.where(Book.year == query_params["year"])
    if query_params["language"]:
        query = query.where(Book.language.ilike(f'%{query_params["language"]}%'))
    if query_params["pages_gt"]:
        query = query.where(Book.pages > query_params["pages_gt"])
    if query_params["pages_lt"]:
        query = query.where(Book.pages < query_params["pages_lt"])
    if query_params["description"]:
        query = query.where(Book.description.ilike(f'%{query_params["description"]}%'))
    if query_params["only_private"]:
        query = query.where(Book.private.is_(True))
    if query_params["tags"]:
        tags = list(map(lambda x: x.lower(), query_params["tags"]))
        query = query.join(Book.tags).where(func.lower(Tag.name).in_(tags))
    return query


async def delete_book(session: AsyncSession, book_id: int) -> None:
    """Удаление книги, её файла и всех превью"""
    book = await get_book(session, book_id)
    await book.delete(session)
    shutil.rmtree(settings.media_root / "books" / str(book_id))
    shutil.rmtree(settings.media_root / "previews" / str(book_id))


@cached(60 * 60 * 24, "recent_books", variable_positions=[2])
async def get_recent_books(session: AsyncSession, limit: int) -> list[BookSchema]:
    query = select(Book).order_by(Book.id.desc()).limit(limit)
    result = await session.execute(query)
    result.unique()
    books = result.scalars().all()
    books_schemas = [BookSchema.model_validate(book) for book in books]
    for book in books_schemas:
        book.preview_image = get_thumbnail(book.preview_image, "small")
    return books_schemas


async def delete_recent_books_cache() -> None:
    await get_cache().delete_namespace("recent_books")
