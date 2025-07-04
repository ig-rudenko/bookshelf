from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import query_count
from app.media_storage.media import get_media_url
from app.models import Book, UserData
from app.orm.query_formats import filter_books_by_user
from app.schemas.books import BookWithReadPagesSchema, BooksWithReadPagesPaginatedSchema
from app.schemas.pdf_history import PDFHistoryFilesSchema, PdfJSHistorySchema, CreatePdfJSHistorySchema
from app.services.paginator import paginate, PaginatorQuery
from app.services.thumbnail import get_thumbnail


async def get_last_viewed_books(
    session: AsyncSession, user_id: int, paginator: PaginatorQuery
) -> BooksWithReadPagesPaginatedSchema:
    """
    Асинхронно получает информацию о последних просмотренных книгах пользователя,
    включая страницу, на которой он остановился.

    Функция извлекает данные о пользователях из базы данных и применяет пагинацию к результатам.

    :param session: Асинхронный объект :class:`AsyncSession` сеанса базы данных.
    :param user_id: Идентификатор пользователя.
    :param paginator:
        Словарь, содержащий информацию о странице и количестве элементов на странице для пагинации:
        - page: Номер текущей страницы (:class:`int`).
        - per_page: Количество элементов на странице (:class:`int`).

    :return: :class:`BooksWithReadPagesPaginatedSchema`, содержащий:
            - books: Список объектов :class:`BookWithReadPagesSchema`,
                     представляющих книги с номером последней прочитанной страницы.
            - total_count: Общее количество книг пользователя.
            - current_page: Номер текущей страницы.
            - max_pages: Общее количество страниц на основе пагинации.
            - per_page: Количество элементов на странице.
    """

    query = (
        select(Book, UserData)
        .join(UserData)
        .where(UserData.user_id == user_id)
        .group_by(UserData)  # type: ignore
        .group_by(Book.id)
        .order_by(UserData.pdf_history_updated_at.desc())
    )
    query = filter_books_by_user(query, user_id)
    query = paginate(query, page=paginator["page"], per_page=paginator["per_page"])

    result = await session.execute(query)
    result.unique()
    count = await query_count(query, session)

    books_schemas = []
    for book, user_data in result.all():  # type: Book, UserData
        try:
            history = PDFHistoryFilesSchema.model_validate_json(user_data.pdf_history)
        except ValueError as e:
            print(e)
        else:
            if history.files:
                schema = BookWithReadPagesSchema.model_validate(book)
                schema.read_pages = history.files[-1].page
                schema.last_time_read = user_data.pdf_history_updated_at
                schema.preview_image = get_media_url(get_thumbnail(book.preview_image, "medium"))
                books_schemas.append(schema)

    return BooksWithReadPagesPaginatedSchema(
        books=books_schemas,
        total_count=count,
        current_page=paginator["page"],
        max_pages=count // paginator["per_page"] or 1,
        per_page=paginator["per_page"],
    )


async def get_pdf_history_data(session: AsyncSession, user_id: int, book_id: int) -> PdfJSHistorySchema:
    """
    Асинхронно получает историю просмотра PDF-файла пользователя для книги.

    :param session: Асинхронный объект :class:`AsyncSession` сеанса базы данных.
    :param user_id: Идентификатор пользователя (:class:`int`).
    :param book_id: Идентификатор книги (:class:`int`).

    :return: :class:`PdfJSHistorySchema`.
    :raises HTTPException: :class:`HTTPException` Пользовательские данные не существуют.
    """
    try:
        user_data = await UserData.get(session, user_id=user_id, book_id=book_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Пользовательские данные не существуют")
    return PdfJSHistorySchema.model_validate(user_data)


async def set_pdf_history_data(
    session: AsyncSession, user_id: int, book_id: int, data: CreatePdfJSHistorySchema
) -> PdfJSHistorySchema:
    """
    Асинхронно создает историю просмотра PDF-файла пользователя для книги.
    Если книга уже имеет историю просмотра, то она будет обновлена, иначе создается новая.

    :param session: Асинхронный объект :class:`AsyncSession` сеанса базы данных.
    :param user_id: Идентификатор пользователя (:class:`int`).
    :param book_id: Идентификатор книги (:class:`int`).
    :param data: :class:`CreatePdfJSHistorySchema`.

    :return: :class:`PdfJSHistorySchema`.
    """
    now = datetime.now(tz=timezone.utc).replace(tzinfo=None)
    try:
        user_data = await UserData.get(session, user_id=user_id, book_id=book_id)
    except NoResultFound:
        user_data = await UserData.create(
            session,
            pdf_history=data.pdf_history,
            pdf_history_updated_at=now,
            user_id=user_id,
            book_id=book_id,
        )
    else:
        user_data.pdf_history = data.pdf_history
        user_data.pdf_history_updated_at = now
        await user_data.save(session)

    return PdfJSHistorySchema.model_validate(user_data)
