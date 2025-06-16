from typing import TypeVar, TypedDict, BinaryIO

# noinspection PyPackageRequirements
import fitz
from fastapi import UploadFile, HTTPException
from sqlalchemy import select, func, Select, delete
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.crud.base import query_count
from app.media_storage import get_storage, AbstractStorage
from app.media_storage.media import get_media_url
from app.models import (
    Book,
    User,
    Tag,
    Publisher,
    UserData,
    favorite_books_association,
    books_read_association,
    Bookshelf,
    BookshelfBookAssociation,
)
from app.orm.query_formats import filter_books_by_user
from app.orm.session_manager import scoped_session
from app.schemas.books import (
    BookSchema,
    BooksSchemaPaginated,
    BookSchemaDetail,
    CreateBookSchema,
    BookshelfLinkSchema,
    PublisherSchema,
    TagSchema,
)
from app.services.cache import get_cache
from app.services.cache.deco import cached
from app.services.paginator import paginate
from app.services.publishers import get_or_create_publisher
from app.services.thumbnail import get_thumbnail

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
        book.preview_image = get_media_url(get_thumbnail(book.preview_image, "medium"))

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
    user_id: int | None,
    query_params: QueryParams,
) -> BooksSchemaPaginated:
    """
    Возвращает отфильтрованные книги в формате :class:`BooksSchemaPaginated` по запросу query_params.

    Если пользователь не указан, то возвращаются только общедоступные книги.

    Если пользователь указан, то возвращаются еще и книги, которые принадлежат пользователю.

    :param session: :class:`AsyncSession` объект сессии.
    :param user_id: Идентификатор пользователя.
    :param query_params: Параметры запроса.
    :return: :class:`BooksSchemaPaginated`
    """

    query = select(Book).order_by(Book.year.desc(), Book.id.desc()).group_by(Book.id)
    query = _filter_books_query_by_params(query, query_params)
    query = filter_books_by_user(query, user_id)

    return await get_paginated_books(session, query, query_params)


async def set_file(session: AsyncSession, file: UploadFile, book: Book):
    """
    Загружает файл в хранилище и сохраняем его размер и ссылку на него в БД.
    :param session: :class:`AsyncSession`.
    :param file: Файл книги.
    :param book: Объект книги.
    """
    storage = get_storage()
    book.file = (await storage.upload_book(file, book.id))[:512]
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

    # noinspection PyArgumentList
    async with scoped_session() as session:
        book = await Book.get(session, id=book_id)
        book.preview_image = preview_name
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


@cached(60 * 60 * 24, "recent_books", variable_positions=[2, 3])
async def get_recent_books(session: AsyncSession, limit: int, user_id: int | None) -> list[BookSchema]:
    query = select(Book).order_by(Book.id.desc()).limit(limit)
    query = filter_books_by_user(query, user_id)

    result = await session.execute(query)
    result.unique()
    books = result.scalars().all()
    books_schemas = [BookSchema.model_validate(book) for book in books]
    for book in books_schemas:
        book.preview_image = get_media_url(get_thumbnail(book.preview_image, "medium"))
    return books_schemas


async def delete_recent_books_cache() -> None:
    await get_cache().delete_namespace("recent_books")


async def get_book(session: AsyncSession, book_id: int) -> Book:
    try:
        return await Book.get(session, id=book_id)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Книга с ID '{book_id}' не найдена"
        )


async def get_book_detail(session: AsyncSession, book_id: int, user_id: int | None) -> BookSchemaDetail:
    """
    Возвращает детальную информацию о книге с отметками просмотра и статуса избранного.
    """
    try:
        query = (
            select(
                Book.id,
                Book.title,
                Book.user_id,
                Book.preview_image,
                Book.authors,
                Book.description,
                Book.pages,
                Book.size,
                Book.year,
                Book.private,
                Book.language,
                Publisher.id.label("publisher_id"),
                Publisher.name.label("publisher_name"),
                func.json_agg(func.json_build_object("id", Tag.id, "name", Tag.name)).label("tags"),
                func.bool(favorite_books_association.c.id).label("is_favorite"),
                func.bool(books_read_association.c.id).label("is_read"),
                func.json_agg(func.json_build_object("id", Bookshelf.id, "name", Bookshelf.name)).label(
                    "bookshelf_info"
                ),
            )
            .where(Book.id == book_id)
            .outerjoin(Book.publisher)
            .outerjoin(Book.tags)
            .outerjoin(
                BookshelfBookAssociation,
                BookshelfBookAssociation.book_id == Book.id,
            )
            .outerjoin(
                Bookshelf,
                Bookshelf.id == BookshelfBookAssociation.bookshelf_id,
            )
            .outerjoin(
                favorite_books_association,
                (
                    (Book.id == favorite_books_association.columns.book_id)
                    & (favorite_books_association.columns.user_id == user_id)
                ),
            )
            .outerjoin(
                books_read_association,
                (
                    (Book.id == books_read_association.c.book_id)
                    & (books_read_association.c.user_id == user_id)
                ),
            )
            .group_by(
                Book.id,
                Publisher.id,
                favorite_books_association.c.id,
                books_read_association.c.id,
            )
        )
        query = filter_books_by_user(query, user_id)

        result = await session.execute(query)
        data = result.one()
        schema = BookSchemaDetail(
            id=data.id,
            title=data.title,
            user_id=data.user_id,
            preview_image=get_media_url(data.preview_image),
            authors=data.authors,
            description=data.description,
            pages=data.pages,
            size=data.size,
            year=data.year,
            private=data.private,
            language=data.language,
            favorite=bool(data.is_favorite),
            read=bool(data.is_read),
            publisher=PublisherSchema(
                id=data.publisher_id,
                name=data.publisher_name,
            ),
            tags=[
                TagSchema(
                    id=tag_info["id"],
                    name=tag_info["name"],
                )
                for tag_info in data.tags
            ],
            bookshelves=[
                BookshelfLinkSchema(
                    id=bookshelf_info["id"],
                    name=bookshelf_info["name"],
                )
                for bookshelf_info in data.bookshelf_info
                if bookshelf_info["id"]
            ],
        )
        return schema

    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Книга не найдена")


async def create_book(session: AsyncSession, user: User, book_data: CreateBookSchema) -> Book:
    publisher = await get_or_create_publisher(session, book_data.publisher, commit=False)
    tags = await _get_or_create_tags(session, book_data.tags, commit=False)
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
    publisher = await get_or_create_publisher(session, book_data.publisher, commit=False)
    tags = await _get_or_create_tags(session, book_data.tags, commit=False)

    book.publisher_id = publisher.id
    book.title = book_data.title
    book.authors = book_data.authors
    book.description = book_data.description
    book.year = book_data.year
    book.language = book_data.language
    book.private = book_data.private
    book.tags = tags
    await book.save(session)
    await session.commit()
    return book


async def _get_or_create_tags(session: AsyncSession, tags: list[str], *, commit: bool = True) -> list[Tag]:
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

    if commit:
        await session.commit()
        for tag in model_tags:
            await session.refresh(tag)

    return model_tags
