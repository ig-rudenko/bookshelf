from typing import TypeVar, TypedDict

from fastapi import HTTPException
from sqlalchemy import Select, select, func, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.schemas.bookshelf import (
    CreateUpdateBookshelfSchema,
    BookshelfSchema,
    BookshelfSchemaSchemaPaginated,
    BookshelfOneBookSchema,
)
from .books import get_book
from .paginator import paginate
from .thumbnail import get_thumbnail
from ..crud.base import query_count
from ..media_storage.media import get_media_url
from ..models import Bookshelf, Book

_QT = TypeVar("_QT", bound=Select)


class QueryParams(TypedDict):
    search: str | None
    page: int
    per_page: int


def _filter_bookselves_query_by_params(query: _QT, query_params: QueryParams) -> _QT:
    """
    Фильтрует запрос по параметрам запроса query_params.
    """
    if query_params["search"]:
        query = query.where(
            Bookshelf.name.ilike(f'%{query_params["search"]}%')
            | Bookshelf.description.ilike(f'%{query_params["search"]}%')
        )
    return query


def _get_bookshelf_schema(data) -> BookshelfSchema:
    """
    Возвращает книгу в формате :class:`BookshelfSchema` по данным из БД.
    """
    return BookshelfSchema(
        id=data.id,
        name=data.name,
        user_id=data.user_id,
        description=data.description,
        created_at=data.created_at,
        books=[
            BookshelfOneBookSchema(
                id=book.get("book_id") or 0,
                preview=get_media_url(get_thumbnail(book["preview_image"], "medium")),
            )
            for book in data.books_info
        ],
    )


async def _get_paginated_bookshelves(
    session: AsyncSession, query: _QT, paginator
) -> BookshelfSchemaSchemaPaginated:
    """
    Возвращает книги в формате :class:`BooksSchemaPaginated` по запросу query и paginator.
    :param session: :class:`AsyncSession` объект сессии.
    :param query: Запрос к БД типа :class:`sqlalchemy.sql.selectable.Select`
    :param paginator: Параметры страницы. Словарь с ключами page, per_page.
    :return:
    """
    query = paginate(query, page=paginator["page"], per_page=paginator["per_page"])
    print(query)
    res = await session.execute(query)
    count = await query_count(query, session)

    result = list(res)
    print(result)
    bookshelves = [_get_bookshelf_schema(row) for row in result]

    return BookshelfSchemaSchemaPaginated(
        bookshelves=bookshelves,
        total_count=count,
        current_page=paginator["page"],
        max_pages=count // paginator["per_page"] or 1,
        per_page=paginator["per_page"],
    )


def _get_bookshelf_query() -> Select:
    """
    Возвращает запрос к БД для получения списка книжных полок.
    """
    return (
        select(
            Bookshelf.id,
            Bookshelf.name,
            Bookshelf.user_id,
            Bookshelf.description,
            Bookshelf.created_at,
            func.array_agg(
                func.json_build_object("book_id", Book.id, "preview_image", Book.preview_image)
            ).label("books_info"),
        )
        .outerjoin(Bookshelf.books)
        .group_by(Bookshelf.id)
    )


async def get_bookshelf(session: AsyncSession, bookshelf_id: int) -> BookshelfSchema:
    """
    Возвращает книжную полку по ID.
    :param session: :class:`AsyncSession` объект сессии.
    :param bookshelf_id: ID книжной полки.
    :return: :class:`BookshelfSchema`
    """
    query = _get_bookshelf_query().where(Bookshelf.id == bookshelf_id)
    result = (await session.execute(query)).one_or_none()
    if result is None:
        raise HTTPException(status_code=404, detail=f"Книжная полка с ID '{bookshelf_id}' не найдена")
    return _get_bookshelf_schema(result)


async def get_filtered_bookshelves(session: AsyncSession, query_params: QueryParams):
    """
    Возвращает список книжных полок по параметрам запроса query_params.
    :param session: :class:`AsyncSession` объект сессии.
    :param query_params: Параметры запроса.
    :return: :class:`BookshelfSchemaSchemaPaginated`
    """
    query = _get_bookshelf_query()
    query = _filter_bookselves_query_by_params(query, query_params)
    return await _get_paginated_bookshelves(session, query, query_params)


async def create_bookshelf(
    session: AsyncSession, user_id: int, bookshelf_schema: CreateUpdateBookshelfSchema
) -> BookshelfSchema:
    """
    Создает книжную полку.
    :param session: :class:`AsyncSession` объект сессии.
    :param user_id: ID пользователя.
    :param bookshelf_schema: :class:`CreateUpdateBookshelfSchema` с данными для создания книжной полки.
    :return: :class:`BookshelfSchema`.
    :raises: HTTPException если недостаточно прав для выполнения операции.
    """

    books = [await get_book(session, book_id) for book_id in bookshelf_schema.books]

    bookshelf = Bookshelf(
        name=bookshelf_schema.name,
        description=bookshelf_schema.description,
        user_id=user_id,
        books=books,
    )
    session.add(bookshelf)

    # Применяем изменения
    try:
        await session.flush()
    except IntegrityError:
        raise HTTPException(status_code=422, detail="Bookshelf с таким именем уже существует")

    await session.commit()

    return BookshelfSchema(
        id=bookshelf.id,
        name=bookshelf.name,
        description=bookshelf.description,
        user_id=bookshelf.user_id,
        created_at=bookshelf.created_at,
        books=[
            BookshelfOneBookSchema(
                id=book.id,
                preview=get_media_url(get_thumbnail(book.preview_image, "medium")),
            )
            for book in books
        ],
    )


async def update_bookshelf(
    session: AsyncSession, bookshelf_id: int, user_id: int, bookshelf_schema: CreateUpdateBookshelfSchema
) -> CreateUpdateBookshelfSchema:
    """
    Обновляет книжную полку.
    :param session: :class:`AsyncSession` объект сессии.
    :param bookshelf_id: ID книжной полки.
    :param user_id: ID пользователя.
    :param bookshelf_schema: :class:`CreateUpdateBookshelfSchema` с данными для обновления книжной полки.
    :return: :class:`CreateUpdateBookshelfSchema`
    :raises: HTTPException если книжная полка не найдена, если недостаточно прав для выполнения операции.
    """
    # Получение книжной полки по ID
    result = await session.execute(
        select(Bookshelf).where(Bookshelf.id == bookshelf_id).options(selectinload(Bookshelf.books))
    )
    bookshelf: Bookshelf | None = result.scalar()
    if bookshelf is None:
        raise HTTPException(status_code=404, detail=f"Книжная полка с ID '{bookshelf_id}' не найдена")

    # Проверка прав доступа
    if bookshelf.user_id != user_id:
        raise HTTPException(status_code=403, detail="Недостаточно прав для выполнения операции")

    # Получение книг и обновление связи
    books = [await get_book(session, book_id) for book_id in bookshelf_schema.books]

    # Обновление полей книжной полки
    bookshelf.name = bookshelf_schema.name
    bookshelf.description = bookshelf_schema.description

    # Обновление связи между книжной полкой и книгами
    for book in set(books) | set(bookshelf.books):
        if book in books and book not in bookshelf.books:
            bookshelf.books.append(book)
        if book not in books:
            bookshelf.books.remove(book)

    # Применение изменений
    try:
        await session.flush()  # Попробуем зафиксировать изменения, чтобы поймать потенциальные ошибки
    except IntegrityError:
        raise HTTPException(status_code=422, detail="Bookshelf с таким именем уже существует")

    await session.commit()

    return bookshelf_schema


async def delete_bookshelf(session: AsyncSession, bookshelf_id: int) -> None:
    """
    Удаляет книжную полку.
    :param session: :class:`AsyncSession` объект сессии.
    :param bookshelf_id: ID книжной полки.
    :return: None
    :raises: HTTPException если книжная полка не найдена.
    """
    # Поиск книжной полки по ID
    query = select(Bookshelf).where(Bookshelf.id == bookshelf_id)
    bookshelf = (await session.execute(query)).scalar_one_or_none()

    if not bookshelf:
        raise HTTPException(status_code=404, detail=f"Книжная полка с ID '{bookshelf_id}' не найдена")

    # Удаление книжной полки
    await session.execute(delete(Bookshelf).where(Bookshelf.id == bookshelf_id))

    # Фиксация изменений в БД
    await session.commit()
