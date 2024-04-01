from sqlalchemy import select

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


async def get_non_private_books() -> list[BookSchema]:
    """Возвращает список всех книг, которые являются публичными"""
    async with db_conn.session as session:
        result = await session.execute(select(Book).where(Book.private.is_(False)))
        result.unique()
        return result.scalars()


async def get_books_with_user_private(user_id: int) -> list[BookSchema]:
    """Возвращает список всех книг, которые являются публичными или принадлежат пользователю"""
    async with db_conn.session as session:
        query = select(Book).where(
            Book.private.is_(False) | (Book.private.is_(True) & (Book.user_id == user_id))
        )
        result = await session.execute(query)
        result.unique()
        return result.scalars()
