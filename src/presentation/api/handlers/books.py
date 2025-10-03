from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from fastapi.responses import StreamingResponse
from slugify import slugify

from src.application.books.commands import (
    CreateBookCommand,
    DeleteBookCommand,
    UpdateBookCommand,
    UploadBookFileCommand,
)
from src.application.books.handlers import BookCommandHandler, BookQueryHandler
from src.application.services.storage import AbstractStorage
from src.application.users.dto import UserDTO
from src.domain.books.entities import BookFilter
from src.presentation.api.auth import get_current_user, get_user_or_none
from src.presentation.api.dependencies import get_book_command_handler, get_book_query_handler, get_storage
from src.presentation.api.handlers.queries import PaginatorQuery, paginator_query
from src.presentation.api.schemas.books import (
    BookSchema,
    BookSchemaDetail,
    BookSchemaWithDesc,
    BooksSchemaPaginated,
    BooksWithReadPagesPaginatedSchema,
    BookWithReadPagesSchema,
    CreateBookSchema,
)

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/recent", response_model=list[BookSchema])
async def get_recent_books_view(
    current_user: Annotated[UserDTO | None, Depends(get_user_or_none)],
    query_handler: Annotated[BookQueryHandler, Depends(get_book_query_handler)],
):
    """Последние 25 добавленных книг."""
    books = await query_handler.handle_get_recent_books(current_user.id if current_user else None)
    return books


@router.get("/publishers", response_model=list[str])
async def get_publishers_view(
    current_user: Annotated[UserDTO | None, Depends(get_user_or_none)],
    query_handler: Annotated[BookQueryHandler, Depends(get_book_query_handler)],
    name: Annotated[str | None, Query(description="Издательство")] = None,
):
    """Поиск издательств по названию."""
    return await query_handler.handle_get_publishers(
        search=name, user_id=current_user.id if current_user else None
    )


@router.get("/authors", response_model=list[str])
async def get_authors_view(
    current_user: Annotated[UserDTO | None, Depends(get_user_or_none)],
    query_handler: Annotated[BookQueryHandler, Depends(get_book_query_handler)],
    name: Annotated[str | None, Query(description="Авторы книги")] = None,
):
    """Поиск авторов по названию."""
    return await query_handler.handle_get_authors(
        search=name, user_id=current_user.id if current_user else None
    )


@router.get("/last-viewed", response_model=BooksWithReadPagesPaginatedSchema)
async def get_last_viewed_books_view(
    paginator: Annotated[PaginatorQuery, Depends(paginator_query)],
    user: Annotated[UserDTO, Depends(get_current_user)],
    query_handler: Annotated[BookQueryHandler, Depends(get_book_query_handler)],
):
    """Возвращает просмотренные книги пользователя с кол-вом просмотренных страниц."""
    result, count = await query_handler.handler_get_last_viewed_books(
        user.id, paginator.page, paginator.per_page
    )
    return BooksWithReadPagesPaginatedSchema(
        books=[BookWithReadPagesSchema.model_validate(book) for book in result],
        total_count=count,
        current_page=paginator.page,
        max_pages=(
            count // paginator.per_page + 1 if count % paginator.per_page else count // paginator.per_page
        ),
        per_page=paginator.per_page,
    )


def books_query_params(
    paginator: Annotated[PaginatorQuery, Depends(paginator_query)],
    search: Annotated[str | None, Query(max_length=254, description="Поиск по названию и описанию")] = None,
    title: Annotated[str | None, Query(max_length=254, description="Заголовок")] = None,
    authors: Annotated[str | None, Query(max_length=254, description="Авторы книги")] = None,
    publisher: Annotated[str | None, Query(max_length=128, description="Издательство")] = None,
    year: Annotated[int | None, Query(gt=0, description="Год издания")] = None,
    language: Annotated[str | None, Query(max_length=128, description="Язык книги")] = None,
    pages_gt: Annotated[
        int | None, Query(gt=0, alias="pages-gt", description="Количество страниц больше чем")
    ] = None,
    pages_lt: Annotated[
        int | None, Query(gt=0, alias="pages-lt", description="Количество страниц меньше чем")
    ] = None,
    description: Annotated[str | None, Query(description="Описание книги")] = None,
    only_private: Annotated[
        bool | None, Query(alias="only-private", description="Только приватные книги")
    ] = False,
    tags: Annotated[list[str] | None, Query(description="Теги книги")] = None,
) -> BookFilter:
    """Параметры поиска по книгам."""

    if pages_gt and pages_lt and pages_gt >= pages_lt:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="pages_gt must be less than pages_lt",
        )
    return BookFilter(
        search=search,
        title=title,
        authors=authors,
        publisher=publisher,
        year=year,
        language=language,
        pages_gt=pages_gt,
        pages_lt=pages_lt,
        description=description,
        only_private=only_private,
        tags=tags,
        page=paginator.page,
        page_size=paginator.per_page,
    )


@router.get("", response_model=BooksSchemaPaginated)
async def get_books_view(
    query_params: Annotated[BookFilter, Depends(books_query_params)],
    current_user: Annotated[UserDTO | None, Depends(get_user_or_none)],
    book_query_handler: Annotated[BookQueryHandler, Depends(get_book_query_handler)],
):
    """Просмотр всех книг с фильтрацией по запросу."""
    query_params.viewer_id = current_user.id if current_user else None
    books, count = await book_query_handler.handle_get_list_books(query_params)

    return BooksSchemaPaginated.from_books_dto(
        books=books,
        total_count=count,
        current_page=query_params.page,
        per_page=query_params.page_size,
    )


@router.post("", response_model=BookSchemaWithDesc, status_code=status.HTTP_201_CREATED)
async def create_book_view(
    book_data: CreateBookSchema,
    current_user: Annotated[UserDTO, Depends(get_current_user)],
    book_command_handler: Annotated[BookCommandHandler, Depends(get_book_command_handler)],
):
    """Создание книги"""
    book = await book_command_handler.handle_create(
        CreateBookCommand(
            user=current_user,
            publisher=book_data.publisher,
            title=book_data.title,
            authors=book_data.authors,
            description=book_data.description,
            year=book_data.year,
            private=book_data.private,
            language=book_data.language,
            tags=book_data.tags,
        )
    )
    return book


@router.get("/{book_id}", response_model=BookSchemaDetail)
async def get_book_view(
    book_id: int,
    current_user: Annotated[UserDTO, Depends(get_current_user)],
    book_query_handler: Annotated[BookQueryHandler, Depends(get_book_query_handler)],
):
    """Просмотр книги"""
    user_id = current_user.id if current_user else None
    return await book_query_handler.handle_get_book_detail(book_id, user_id)


@router.put("/{book_id}", response_model=BookSchemaWithDesc)
async def update_book_view(
    book_id: int,
    book_data: CreateBookSchema,
    current_user: Annotated[UserDTO, Depends(get_current_user)],
    book_command_handler: Annotated[BookCommandHandler, Depends(get_book_command_handler)],
):
    """Обновление книги"""
    book = await book_command_handler.handle_update(
        UpdateBookCommand(
            user=current_user,
            book_id=book_id,
            publisher=book_data.publisher,
            title=book_data.title,
            authors=book_data.authors,
            description=book_data.description,
            year=book_data.year,
            private=book_data.private,
            language=book_data.language,
            tags=book_data.tags,
        )
    )
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book_view(
    book_id: int,
    current_user: Annotated[UserDTO, Depends(get_current_user)],
    book_command_handler: Annotated[BookCommandHandler, Depends(get_book_command_handler)],
):
    """Удаление книги"""
    await book_command_handler.handle_delete(
        DeleteBookCommand(
            user=current_user,
            book_id=book_id,
        )
    )


@router.post("/{book_id}/upload", response_model=BookSchema)
async def upload_book_file(
    book_id: int,
    file: UploadFile,
    current_user: Annotated[UserDTO, Depends(get_current_user)],
    book_command_handler: Annotated[BookCommandHandler, Depends(get_book_command_handler)],
):
    """Загрузка файла книги"""
    if file.filename is None or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Формат файла должен быть только '.pdf'"
        )
    book = await book_command_handler.handler_upload_file(
        UploadBookFileCommand(user=current_user, book_id=book_id, file=file)
    )
    return book


@router.get("/{book_id}/download", response_class=StreamingResponse)
async def download_book_file(
    book_id: int,
    user: Annotated[UserDTO | None, Depends(get_user_or_none)],
    book_query_handler: Annotated[BookQueryHandler, Depends(get_book_query_handler)],
    storage: Annotated[AbstractStorage, Depends(get_storage)],
    as_file: Annotated[bool, Query(alias="as-file")] = False,
):
    """Скачивание файла книги"""
    book = await book_query_handler.handle_get_book(book_id)
    if book.private and (user is None or book.user_id != user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на скачивание файла данной книги",
        )

    headers = {
        "Cache-Control": "max-age=86400",
    }
    if as_file:
        headers["Content-Disposition"] = f'attachment; filename="{slugify(book.title)}.pdf"'

    try:
        book_async_iterator = storage.get_book_iterator(book.id)
    except storage.FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Файл книги не найден") from exc

    return StreamingResponse(
        content=book_async_iterator,
        media_type="application/pdf",
        headers=headers,
    )
