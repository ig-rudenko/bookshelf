from typing import TypedDict, TypeVar

from sqlalchemy import select, func, ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.connector import db_conn
from ..models import Publisher, Tag, Book, User
from ..schemas.books import CreateBookSchema, BookSchema


async def create_book(user: User, book_data: CreateBookSchema) -> Book:
    async with db_conn.session as conn:
        publisher = await _get_or_create_publisher(book_data.publisher, conn)
        tags = await _get_or_create_tags(book_data.tags, conn)
        book = Book(
            user_id=user.id,
            publisher=publisher,
            title=book_data.title,
            preview_image="",
            file="",
            authors=book_data.authors,
            description=book_data.description,
            pages=1,
            size=1,
            year=book_data.year,
            private=book_data.private,
            language=book_data.language,
            tags=tags,
        )
        conn.add(publisher)
        conn.add_all(tags)
        conn.add(book)
        await conn.commit()
        await conn.refresh(book)
        return book


async def update_book(book: Book, book_data: CreateBookSchema) -> Book:
    async with db_conn.session as conn:
        publisher = await _get_or_create_publisher(book_data.publisher, conn)
        tags = await _get_or_create_tags(book_data.tags, conn)
        book.publisher = publisher
        book.title = book_data.title
        book.authors = book_data.authors
        book.description = book_data.description
        book.year = book_data.year
        book.tags = tags

        conn.add(publisher)
        conn.add_all(tags)
        conn.add(book)
        await conn.commit()
        await conn.refresh(book)
        return book


async def _get_or_create_tags(tags: list[str], conn) -> list[Tag]:
    """Находит или создает список тегов"""
    model_tags = []
    for tag_name in tags:
        result = await conn.execute(select(Tag).where(Tag.name.ilike(tag_name)))
        result.unique()
        tag = result.scalar_one_or_none()
        if tag is None:
            tag = Tag(name=tag_name)

        model_tags.append(tag)

    return model_tags


async def _get_or_create_publisher(publisher_name: str, conn) -> Publisher:
    """Находит или создает издательство по названию"""
    query = select(Publisher).where(Publisher.name.ilike(publisher_name))
    result = await conn.execute(query)
    result.unique()
    publisher = result.scalar_one_or_none()
    if publisher is None:
        publisher = Publisher(name=publisher_name)

    return publisher


class QueryParams(TypedDict):
    title: str
    authors: str
    publisher: str
    year: int
    language: str
    pages_gt: int
    pages_lt: int
    description: str
    only_private: bool
    tags: list[str]
    page: int
    per_page: int


QT = TypeVar("QT")


def filter_book_query(query: QT, query_params: QueryParams) -> QT:
    if query_params["title"]:
        query = query.where(Book.title.ilike(f'%{query_params["title"]}%'))
    if query_params["authors"]:
        query = query.where(Book.authors.ilike(f'%{query_params["authors"]}%'))
    if query_params["publisher"]:
        query = query.where(Book.publisher.name.ilike(f'%{query_params["publisher"]}%'))
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
        query = query.join(Book.tags).where(Tag.name.in_(query_params["tags"])).group_by(Book.id)
    if query_params["page"] and query_params["per_page"]:
        per_page = query_params["per_page"]
        page = query_params["page"]
        query = query.offset((page - 1) * per_page).limit(per_page)
    return query


async def get_non_private_books(query_params: QueryParams) -> tuple[ScalarResult[BookSchema], int]:
    """Возвращает список книг и количество, которые являются публичными"""
    async with db_conn.session as session:
        query = filter_book_query(select(Book), query_params).where(Book.private.is_(False))
        result = await session.execute(query)
        result.unique()
        books = result.scalars()
        books_count = await _get_books_count_for_query(query_params, session)
    return books, books_count


async def get_books_with_user_private(
    user_id: int, query_params: QueryParams
) -> tuple[ScalarResult[BookSchema], int]:
    """Возвращает список книг и количество, которые являются публичными или принадлежат пользователю"""
    async with db_conn.session as session:
        query = filter_book_query(select(Book), query_params)
        query = query.where(Book.private.is_(False) | (Book.private.is_(True) & (Book.user_id == user_id)))
        result = await session.execute(query)
        result.unique()
        books = result.scalars()
        books_count = await _get_books_count_for_query(query_params, session)
    return books, books_count


async def _get_books_count_for_query(query_params: QueryParams, session: AsyncSession) -> int:
    """Определяет количество книг для запроса"""
    count_query = filter_book_query(select(func.count(Book.id)), query_params).limit(None).offset(None)
    count_result = await session.execute(count_query)
    count_result.unique()
    return count_result.scalar_one_or_none() or 0
