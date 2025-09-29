from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy import or_, select, func, over, Select
from sqlalchemy.exc import IntegrityError as SQLAlchemyIntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.bookshelves.entities import Bookshelf, BookshelfFilter, BookValue
from src.domain.bookshelves.repository import BookshelfRepository
from src.domain.common.exceptions import ObjectNotFoundError
from src.infrastructure.db.exception_handler import wrap_sqlalchemy_exception
from src.infrastructure.db.models import BookshelfModel, BookshelfBookAssociationModel, BookModel


class _SQLBookshelfRepository(SQLAlchemyAsyncRepository[BookshelfModel]):
    model_type = BookshelfModel

    @property
    def dialect(self):
        return self._dialect.name


class SqlAlchemyBookshelfRepository(BookshelfRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self._repo = _SQLBookshelfRepository(
            session=session, auto_commit=False, auto_refresh=True, wrap_exceptions=False
        )

    async def get(self, bookshelf_id: int) -> Bookshelf:
        with wrap_sqlalchemy_exception(self._repo.dialect):
            result = await self.session.execute(self._get_query().where(BookshelfModel.id == bookshelf_id))
            return self._to_domain(result.one())

    async def get_filtered(self, filter_: BookshelfFilter) -> tuple[list[Bookshelf], int]:
        offset = (filter_.page - 1) * filter_.page_size
        query = self._get_query().add_columns(over(func.count()).label("count"))
        query = query.limit(filter_.page_size).offset(offset)

        if filter_.viewer_id:
            query = query.where(
                BookshelfModel.private.is_(False)
                | (BookshelfModel.private.is_(True) & (BookshelfModel.user_id == filter_.viewer_id))
            )
        else:
            query = query.where(BookshelfModel.private.is_(False))
        if filter_.search:
            query = query.where(
                or_(
                    BookshelfModel.name.ilike(f"%{filter_.search}%"),
                    BookshelfModel.description.ilike(f"%{filter_.search}%"),
                )
            )
        if filter_.is_private:
            query = query.where(BookshelfModel.private == filter_.is_private)
        if filter_.user_id:
            query = query.where(BookshelfModel.user_id == filter_.user_id)
        if filter_.book_id:
            query = query.join(
                BookshelfBookAssociationModel, BookshelfBookAssociationModel.bookshelf_id == BookshelfModel.id
            ).where(BookshelfBookAssociationModel.book_id == filter_.book_id)

        with wrap_sqlalchemy_exception(self._repo.dialect):
            result = await self.session.execute(query)
            count: int = 0
            instances: list[Bookshelf] = []
            for i, data in enumerate(result):
                instances.append(
                    Bookshelf(
                        id=data.id,
                        name=data.name,
                        user_id=data.user_id,
                        description=data.description,
                        created_at=data.created_at,
                        private=data.private,
                        books=[
                            BookValue(id=book.get("book_id") or 0, preview=book.get("preview_image", ""))
                            for book in data.books_info
                        ],
                    )
                )
                if i == 0:
                    count = int(data.count)

        return instances, count

    @staticmethod
    def _get_query() -> Select:
        return (
            select(
                BookshelfModel.id,
                BookshelfModel.name,
                BookshelfModel.user_id,
                BookshelfModel.description,
                BookshelfModel.created_at,
                BookshelfModel.private,
                func.array_agg(
                    func.json_build_object("book_id", BookModel.id, "preview_image", BookModel.preview_image)
                ).label("books_info"),
            )
            .outerjoin(BookshelfModel.books)
            .group_by(BookshelfModel.id)
        )

    async def add(self, bookshelf: Bookshelf) -> Bookshelf:
        with wrap_sqlalchemy_exception(self._repo.dialect):
            model = await self._repo.add(self._to_model(bookshelf))
            for book in bookshelf.books:
                self.session.add(BookshelfBookAssociationModel(bookshelf_id=model.id, book_id=book.id))
                try:
                    await self.session.flush()
                except SQLAlchemyIntegrityError as exc:
                    raise ObjectNotFoundError(f"Book with id {book.id} not found") from exc
        return bookshelf

    async def update(self, bookshelf: Bookshelf) -> Bookshelf:
        with wrap_sqlalchemy_exception(self._repo.dialect):
            existing_bookshelf = await self.get(bookshelf.id)
            existing_books = {book.id for book in existing_bookshelf.books}
            new_books = {book.id for book in bookshelf.books}

            for book in existing_books | new_books:
                if book in existing_books and book not in new_books:
                    await self.session.delete(
                        BookshelfBookAssociationModel(bookshelf_id=bookshelf.id, book_id=book)
                    )
                if book not in existing_books:
                    self.session.add(BookshelfBookAssociationModel(bookshelf_id=bookshelf.id, book_id=book))
            await self.session.flush()

            await self._repo.update(
                self._to_model(bookshelf),
                attribute_names=[
                    "name",
                    "description",
                    "private",
                ],
            )
            return bookshelf

    async def delete(self, bookshelf_id: int) -> None:
        with wrap_sqlalchemy_exception(self._repo.dialect):
            await self._repo.delete(bookshelf_id)

    @staticmethod
    def _to_model(bookshelf: Bookshelf) -> BookshelfModel:
        return BookshelfModel(
            id=bookshelf.id if bookshelf.id else None,
            name=bookshelf.name,
            description=bookshelf.description,
            user_id=bookshelf.user_id,
            private=bookshelf.private,
        )

    @staticmethod
    def _to_domain(data) -> Bookshelf:
        return Bookshelf(
            id=data.id,
            name=data.name,
            user_id=data.user_id,
            description=data.description,
            created_at=data.created_at,
            private=data.private,
            books=[
                BookValue(id=book.get("book_id") or 0, preview=book.get("preview_image", ""))
                for book in data.books_info
            ],
        )
