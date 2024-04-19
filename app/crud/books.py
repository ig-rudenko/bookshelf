from fastapi import HTTPException, status
from sqlalchemy import select
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
