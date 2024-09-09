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
)
from .books import get_book
from .paginator import paginate
from ..crud.base import query_count
from ..models import Bookshelf, BookshelfBookAssociation

_QT = TypeVar("_QT", bound=Select)


class QueryParams(TypedDict):
    search: str | None
    page: int
    per_page: int


def _filter_bookselves_query_by_params(query: _QT, query_params: QueryParams) -> _QT:
    if query_params["search"]:
        query = query.where(
            Bookshelf.name.ilike(f'%{query_params["search"]}%')
            | Bookshelf.description.ilike(f'%{query_params["search"]}%')
        )
    return query


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
    res = await session.execute(query)
    count = await query_count(query, session)
    bookshelves = [
        BookshelfSchema(
            id=row.id,
            name=row.name,
            user_id=row.user_id,
            description=row.description,
            created_at=row.created_at,
            books=[book_id for book_id in row.book_ids if book_id],
        )
        for row in res.fetchall()
    ]

    return BookshelfSchemaSchemaPaginated(
        bookshelves=bookshelves,
        total_count=count,
        current_page=paginator["page"],
        max_pages=count // paginator["per_page"] or 1,
        per_page=paginator["per_page"],
    )


def _get_bookshelf_query() -> Select:
    return (
        select(
            Bookshelf.id,
            Bookshelf.name,
            Bookshelf.user_id,
            Bookshelf.description,
            Bookshelf.created_at,
            func.array_agg(BookshelfBookAssociation.book_id).label("book_ids"),
        )
        .join(  # Левое соединение, если книжная полка без книг
            BookshelfBookAssociation, Bookshelf.id == BookshelfBookAssociation.bookshelf_id, isouter=True
        )
        .group_by(Bookshelf.id)
    )


async def get_bookshelf(session: AsyncSession, bookshelf_id: int) -> BookshelfSchema:
    query = _get_bookshelf_query()
    result = (await session.execute(query)).one_or_none()
    if result is None:
        raise HTTPException(status_code=404, detail=f"Книжная полка с ID '{bookshelf_id}' не найдена")
    return BookshelfSchema(
        id=result.id,
        name=result.name,
        description=result.description,
        user_id=result.user_id,
        created_at=result.created_at,
        books=result.book_ids,
    )


async def get_filtered_bookshelves(session: AsyncSession, query_params: QueryParams):
    query = _get_bookshelf_query()
    query = _filter_bookselves_query_by_params(query, query_params)
    return await _get_paginated_bookshelves(session, query, query_params)


async def create_bookshelf(
    session: AsyncSession, user_id: int, bookshelf_schema: CreateUpdateBookshelfSchema
) -> BookshelfSchema:

    books = [await get_book(session, book_id) for book_id in bookshelf_schema.books]

    bookshelf = Bookshelf(
        name=bookshelf_schema.name,
        description=bookshelf_schema.description,
        user_id=user_id,
        books=[],
    )
    session.add(bookshelf)

    # Привязываем книги к книжной полке
    bookshelf.books.extend(books)

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
        books=bookshelf_schema.books,
    )


async def update_bookshelf(
    session: AsyncSession, bookshelf_id: int, user_id: int, bookshelf_schema: CreateUpdateBookshelfSchema
) -> CreateUpdateBookshelfSchema:
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
        if book in books:
            bookshelf.books.append(book)
        else:
            bookshelf.books.remove(book)

    # Применение изменений
    try:
        await session.flush()  # Попробуем зафиксировать изменения, чтобы поймать потенциальные ошибки
    except IntegrityError:
        raise HTTPException(status_code=422, detail="Bookshelf с таким именем уже существует")

    await session.commit()

    return bookshelf_schema


async def delete_bookshelf(session: AsyncSession, bookshelf_id: int):
    # Поиск книжной полки по ID
    query = select(Bookshelf).where(Bookshelf.id == bookshelf_id)
    bookshelf = (await session.execute(query)).scalar_one_or_none()

    if not bookshelf:
        raise HTTPException(status_code=404, detail=f"Книжная полка с ID '{bookshelf_id}' не найдена")

    # Удаление книжной полки
    await session.execute(delete(Bookshelf).where(Bookshelf.id == bookshelf_id))

    # Фиксация изменений в БД
    await session.commit()
