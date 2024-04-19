from functools import reduce
from typing import TypedDict, TypeVar

from fastapi import HTTPException, status
from sqlalchemy import select, func, Select, ScalarResult
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Publisher, Tag, Book, User, favorite_books_association, books_read_association
from ..schemas.books import CreateBookSchema, BookSchemaDetail


async def get_book(session: AsyncSession, book_id: int) -> Book:
    try:
        return await Book.get(session, id=book_id)
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена")


async def get_book_detail(session: AsyncSession, book_id: int, user: User | None) -> BookSchemaDetail:
    try:
        query = select(Book, favorite_books_association.columns.id, books_read_association.columns.id).where(
            Book.id == book_id
        )
        query = query.outerjoin(
            favorite_books_association,
            (
                (Book.id == favorite_books_association.columns.book_id)
                & (favorite_books_association.columns.user_id == (user.id if user else None))
            ),
        ).outerjoin(
            books_read_association,
            (
                (Book.id == books_read_association.columns.book_id)
                & (books_read_association.columns.user_id == (user.id if user else None))
            ),
        )
        result = await session.execute(query)
        result.unique()

        data = result.first()
        schema = BookSchemaDetail.model_validate(data[0])
        schema.favorite = data[1] is not None
        schema.read = data[2] is not None
        return schema

    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена")


async def create_book(session: AsyncSession, user: User, book_data: CreateBookSchema) -> Book:
    publisher = await _get_or_create_publisher(session, book_data.publisher)
    tags = await _get_or_create_tags(session, book_data.tags)
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

    book.publisher_id = publisher.id
    book.title = book_data.title
    book.authors = book_data.authors
    book.description = book_data.description
    book.year = book_data.year
    book.language = book_data.language
    book.tags = tags
    await book.save(session)
    await session.commit()
    return book


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
    session.add_all(model_tags)
    return model_tags


async def _get_or_create_publisher(session: AsyncSession, publisher_name: str) -> Publisher:
    """Находит или создает издательство по названию"""
    query = select(Publisher).where(Publisher.name.ilike(publisher_name))
    result = await session.execute(query)
    result.unique()
    publisher = result.scalar_one_or_none()
    if publisher is None:
        publisher = Publisher(name=publisher_name)
        session.add(publisher)
        await session.commit()
        await session.refresh(publisher)

    return publisher


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


QT = TypeVar("QT", bound=Select)


def filter_query_by_params(query: QT, query_params: QueryParams) -> QT:
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
        query = query.join(Book.tags).where(func.lower(Tag.name).in_(tags)).group_by(Book.id)
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

    query = filter_query_by_params(select(Book).order_by(Book.id.desc()), query_params)
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
    counts_list = list(count_result.scalars())
    return reduce(lambda x, y: x + y, counts_list) if counts_list else 0
