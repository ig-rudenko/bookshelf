from typing import TypedDict, TypeVar

from fastapi import HTTPException, status
from sqlalchemy import select, ScalarResult, func, Select, delete
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Publisher, Tag, Book, User
from ..schemas.books import CreateBookSchema


async def get_book(session: AsyncSession, book_id: int) -> Book:
    try:
        return await Book.get(session, id=book_id)
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена")


async def create_book(session: AsyncSession, user: User, book_data: CreateBookSchema) -> Book:
    publisher = await _get_or_create_publisher(session, book_data.publisher)
    session.add(publisher)
    tags = await _get_or_create_tags(session, book_data.tags)
    session.add_all(tags)
    book = Book(
        user_id=user.id,
        publisher_id=publisher.id,
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
    session.add(book)
    await session.commit()
    await session.refresh(book)
    return book


async def update_book(session: AsyncSession, book: Book, book_data: CreateBookSchema) -> Book:
    publisher = await _get_or_create_publisher(session, book_data.publisher)
    tags = await _get_or_create_tags(session, book_data.tags)
    book.publisher = publisher
    book.title = book_data.title
    book.authors = book_data.authors
    book.description = book_data.description
    book.year = book_data.year
    book.tags = tags

    session.add(publisher)
    session.add_all(tags)
    session.add(book)
    await session.commit()
    await session.refresh(book)
    return book


async def delete_book(session: AsyncSession, book_id: int) -> None:
    await session.execute(delete(Book).where(Book.id == book_id))
    await session.commit()


async def _get_or_create_tags(session: AsyncSession, tags: list[str]) -> list[Tag]:
    """Находит или создает список тегов"""
    model_tags = []
    for tag_name in tags:
        result = await session.execute(select(Tag).where(Tag.name.ilike(tag_name)))
        result.unique()
        tag = result.scalar_one_or_none()
        if tag is None:
            tag = Tag(name=tag_name)

        model_tags.append(tag)

    return model_tags


async def _get_or_create_publisher(session: AsyncSession, publisher_name: str) -> Publisher:
    """Находит или создает издательство по названию"""
    query = select(Publisher).where(Publisher.name.ilike(publisher_name))
    result = await session.execute(query)
    result.unique()
    publisher = result.scalar_one_or_none()
    if publisher is None:
        publisher = Publisher(name=publisher_name)

    return publisher


class QueryParams(TypedDict):
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


QT = TypeVar("QT", bound=Select)


def filter_query_by_params(query: QT, query_params: QueryParams) -> QT:
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


async def get_filtered_books_list(
    session: AsyncSession,
    user: User | None,
    query_params: QueryParams,
) -> tuple[ScalarResult[Book], int]:
    """Возвращает список книг и количество, которые являются публичными"""

    def filter_query_by_user(q: QT) -> QT:
        if user is not None:
            return q.where(Book.private.is_(False) | (Book.private.is_(True) & (Book.user_id == user.id)))
        return q.where(Book.private.is_(False))

    query = filter_query_by_params(select(Book), query_params)
    query = filter_query_by_user(query)

    result = await session.execute(query)
    result.unique()
    books = result.scalars()

    books_count: int = await _get_books_count_for_query(
        session,
        filter_query_by_user(select(func.count(Book.id))),
        query_params,
    )
    return books, books_count


async def _get_books_count_for_query(session: AsyncSession, query, query_params: QueryParams) -> int:
    """Определяет количество книг для запроса"""
    count_query = filter_query_by_params(query, query_params).limit(None).offset(None)
    count_result = await session.execute(count_query)
    count_result.unique()
    return count_result.scalar_one_or_none() or 0
