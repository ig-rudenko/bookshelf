from typing import TypeVar, TypedDict, BinaryIO

import fitz
from fastapi import UploadFile
from sqlalchemy import select, func, Select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..crud.base import query_count
from ..crud.books import get_book
from ..media_storage import get_storage, AbstractStorage
from ..models import Book, User, Tag, Publisher, UserData
from ..orm.session_manager import db_manager
from ..schemas.books import BookSchema, BooksSchemaPaginated
from ..services.cache import get_cache, cached
from ..services.paginator import paginate
from ..services.thumbnail import create_thumbnails, get_thumbnail
from ..settings import settings

_QT = TypeVar("_QT", bound=Select)


async def get_paginated_books(session: AsyncSession, query: _QT, paginator) -> BooksSchemaPaginated:
    """
    Возвращает книги в формате :class:`BooksSchemaPaginated` по запросу query и paginator.
    :param session: :class:`AsyncSession` объект сессии.
    :param query: Запрос к БД типа :class:`sqlalchemy.sql.selectable.Select`
    :param paginator: Параметры страницы. Словарь с ключами page, per_page.
    :return:
    """
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
    """
    Возвращает отфильтрованные книги в формате :class:`BooksSchemaPaginated` по запросу query_params.

    Если пользователь не указан, то возвращаются только общедоступные книги.

    Если пользователь указан, то возвращаются еще и книги, которые принадлежат пользователю.

    :param session: :class:`AsyncSession` объект сессии.
    :param user: Пользователь.
    :param query_params: Параметры запроса.
    :return: :class:`BooksSchemaPaginated`
    """

    query = select(Book).order_by(Book.year.desc(), Book.id.desc()).group_by(Book.id)
    query = _filter_books_query_by_params(query, query_params)

    if user is not None:
        query = query.where(Book.private.is_(False) | (Book.private.is_(True) & (Book.user_id == user.id)))
    else:
        query = query.where(Book.private.is_(False))

    return await get_paginated_books(session, query, query_params)


async def set_file(session: AsyncSession, file: UploadFile, book: Book):
    """
    Загружает файл в хранилище и сохраняем его размер и ссылку на него в БД.
    :param session: :class:`AsyncSession`.
    :param file: Файл книги.
    :param book: Объект книги.
    """
    storage = get_storage()
    book.file = await storage.upload_book(file, book.id)
    book.size = file.size or 0
    await book.save(session)


async def create_book_preview_and_update_pages_count(storage: AbstractStorage, book_id: int) -> str:
    """
    Создает превью книги из первой страницы PDF документа и обновляет ее количество страниц в БД.

    :param storage: :class:`AbstractStorage` объект хранилища.
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

    async with db_manager.session() as session:
        book = await Book.get(session, id=book_id)
        book.preview_image = f"{settings.media_url}/{preview_name}"
        book.pages = total_pages
        await book.save(session)
    return preview_name


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
    # Удаляем пользовательские данные, которые связаны с этой книгой.
    await session.execute(delete(UserData).where(UserData.book_id == book.id))
    await book.delete(session)
    await get_storage().delete_book(book.id)


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
