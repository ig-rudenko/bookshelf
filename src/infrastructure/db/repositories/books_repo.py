from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy import Select, delete, distinct, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from src.domain.books.entities import Book, BookFilter, BookmarksQueryFilter, Publisher, Tag
from src.domain.books.repository import BookRepository
from src.infrastructure.db.exception_handler import wrap_sqlalchemy_exception
from src.infrastructure.db.models import (
    BookModel,
    FavoriteBookModel,
    PublisherModel,
    ReadBookModel,
    TagModel,
)


class SQLBookRepository(SQLAlchemyAsyncRepository[BookModel]):
    model_type = BookModel

    @property
    def dialect(self):
        return self._dialect.name


class SqlAlchemyBookRepository(BookRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self._repo = SQLBookRepository(
            session=session, auto_commit=False, auto_refresh=True, wrap_exceptions=False
        )

    async def get_by_id(self, book_id: int) -> Book:
        with wrap_sqlalchemy_exception(self._repo.dialect):
            model = await self._repo.get(book_id, uniquify=True)
            return self._to_domain(model)

    async def get_filtered(self, filter_: BookFilter) -> tuple[list[Book], int]:
        offset = (filter_.page - 1) * filter_.page_size
        query = select(BookModel).group_by(BookModel.id).limit(filter_.page_size).offset(offset)

        for field in filter_.sorted_by:
            if field.startswith("-") and hasattr(BookModel, field[1:]):
                query = query.order_by(getattr(BookModel, field[1:]).desc())
            elif hasattr(BookModel, field):
                query = query.order_by(getattr(BookModel, field).asc())

        if filter_.search:
            query = query.where(
                BookModel.title.ilike(f"%{filter_.search}%")
                | BookModel.description.ilike(f"%{filter_.search}%")
            )
        if filter_.title:
            query = query.where(BookModel.title.ilike(f"%{filter_.title}%"))
        if filter_.authors:
            query = query.where(BookModel.authors.ilike(f"%{filter_.authors}%"))
        if filter_.publisher:
            query = query.join(BookModel.publisher).filter(
                PublisherModel.name.ilike(f"%{filter_.publisher}%")
            )
        if filter_.year is not None:
            query = query.where(BookModel.year == filter_.year)
        if filter_.language:
            query = query.where(BookModel.language.ilike(f"%{filter_.language}%"))
        if filter_.pages_gt is not None:
            query = query.where(BookModel.pages > filter_.pages_gt)
        if filter_.pages_lt is not None:
            query = query.where(BookModel.pages < filter_.pages_lt)
        if filter_.description:
            query = query.where(BookModel.description.ilike(f"%{filter_.description}%"))

        if filter_.only_private is not None and filter_.viewer_id is not None:
            query = query.where(BookModel.private.is_(True), BookModel.user_id == filter_.viewer_id)
        else:
            query = self._filter_books_by_viewer(query, filter_.viewer_id)

        if filter_.tags:
            query = query.join(BookModel.tags)
            for tag in filter_.tags:
                query = query.where(func.lower(TagModel.name) == tag.lower())  # noqa
        if filter_.ids_in:
            query = query.where(BookModel.id.in_(filter_.ids_in))

        with wrap_sqlalchemy_exception(self._repo.dialect):
            results, total = await self._repo.list_and_count(statement=query, uniquify=True)
            return [self._to_domain(r) for r in results], total

    async def add(self, book: Book) -> Book:
        with wrap_sqlalchemy_exception(self._repo.dialect):
            publisher_model = await self._get_or_create_publisher(book.publisher.name)
            tags_models = await self._get_or_create_tags(book.tags)
            book.publisher = Publisher(id=publisher_model.id, name=publisher_model.name)
            book_model = self._to_model(book)
            self.session.add(book_model)
            book_model.tags = tags_models
            await self.session.flush()
            await self.session.refresh(book_model)
            return self._to_domain(book_model)

    async def update(self, book: Book) -> Book:
        with wrap_sqlalchemy_exception(self._repo.dialect):
            publisher_model = await self._get_or_create_publisher(book.publisher.name)
            book.publisher = Publisher(id=publisher_model.id, name=publisher_model.name)
            tags_models = await self._get_or_create_tags(book.tags)
            book.tags = [tag.name for tag in tags_models]

            book_model = self._to_model(book)
            book_model.tags = tags_models
            book_model.publisher_id = publisher_model.id
            book_model = await self._repo.update(book_model)
        return self._to_domain(book_model)

    async def delete(self, book_id: int) -> None:
        with wrap_sqlalchemy_exception(self._repo.dialect):
            await self._repo.delete(book_id)

    async def get_favorite_books(self, filter_: BookmarksQueryFilter) -> tuple[list[Book], int]:
        with wrap_sqlalchemy_exception(self._repo.dialect):
            query = (
                select(BookModel)
                .join(FavoriteBookModel)
                .where(
                    FavoriteBookModel.book_id == BookModel.id,
                    FavoriteBookModel.user_id == filter_.user_id,
                )
                .group_by(BookModel.id, FavoriteBookModel.id)
                .limit(filter_.page_size)
                .order_by(FavoriteBookModel.id.desc())
                .offset((filter_.page - 1) * filter_.page_size)
            )
            result, total = await self._repo.list_and_count(statement=query, uniquify=True)
            return [self._to_domain(book) for book in result], total

    async def update_favorite_status(self, book_id: int, user_id: int, favorite: bool) -> None:
        with wrap_sqlalchemy_exception(self._repo.dialect):
            query = select(FavoriteBookModel.id).where(
                FavoriteBookModel.book_id == book_id,
                FavoriteBookModel.user_id == user_id,
            )
            has_favorite = (await self.session.execute(query)).scalar_one_or_none() is not None
            if favorite and not has_favorite:
                self.session.add(FavoriteBookModel(book_id=book_id, user_id=user_id))
            elif not favorite and has_favorite:
                await self.session.execute(
                    delete(FavoriteBookModel).where(
                        FavoriteBookModel.book_id == book_id,
                        FavoriteBookModel.user_id == user_id,
                    )
                )
            await self.session.flush()

    async def get_favorite_books_count(self, user_id: int) -> int:
        with wrap_sqlalchemy_exception(self._repo.dialect):
            query = (
                select(func.count())
                .select_from(FavoriteBookModel)
                .where(FavoriteBookModel.user_id == user_id)
            )
            result = await self.session.execute(query)
            count = result.scalar_one_or_none()
            return count if count is not None else 0

    async def is_favorite_by_user(self, book_id: int, user_id: int) -> bool:
        with wrap_sqlalchemy_exception(self._repo.dialect):
            query = (
                select(func.count())
                .select_from(FavoriteBookModel)
                .where(
                    FavoriteBookModel.book_id == book_id,
                    FavoriteBookModel.user_id == user_id,
                )
            )
            result = await self.session.execute(query)
            return bool(result.scalar_one_or_none())

    async def get_read_books(self, filter_: BookmarksQueryFilter) -> tuple[list[Book], int]:
        with wrap_sqlalchemy_exception(self._repo.dialect):
            query = (
                select(BookModel)
                .join(ReadBookModel)
                .where(
                    ReadBookModel.book_id == BookModel.id,
                    ReadBookModel.user_id == filter_.user_id,
                )
                .group_by(BookModel.id, ReadBookModel.id)
                .limit(filter_.page_size)
                .order_by(ReadBookModel.id.desc())
                .offset((filter_.page - 1) * filter_.page_size)
            )
            result, total = await self._repo.list_and_count(statement=query, uniquify=True)
            return [self._to_domain(book) for book in result], total

    async def update_read_status(self, book_id: int, user_id: int, read: bool) -> None:
        with wrap_sqlalchemy_exception(self._repo.dialect):
            query = select(ReadBookModel.id).where(
                ReadBookModel.book_id == book_id,
                ReadBookModel.user_id == user_id,
            )
            has_read = (await self.session.execute(query)).scalar_one_or_none() is not None
            if read and not has_read:
                self.session.add(ReadBookModel(book_id=book_id, user_id=user_id))
            elif not read and has_read:
                await self.session.execute(
                    delete(ReadBookModel).where(
                        ReadBookModel.book_id == book_id,
                        ReadBookModel.user_id == user_id,
                    )
                )
            await self.session.flush()

    async def get_read_books_count(self, user_id: int) -> int:
        with wrap_sqlalchemy_exception(self._repo.dialect):
            query = select(func.count()).select_from(ReadBookModel).where(ReadBookModel.user_id == user_id)
            result = await self.session.execute(query)
            count = result.scalar_one_or_none()
            return count if count is not None else 0

    async def is_read_by_user(self, book_id: int, user_id: int) -> bool:
        with wrap_sqlalchemy_exception(self._repo.dialect):
            query = (
                select(func.count())
                .select_from(ReadBookModel)
                .where(
                    ReadBookModel.book_id == book_id,
                    ReadBookModel.user_id == user_id,
                )
            )
            result = await self.session.execute(query)
            return bool(result.scalar_one_or_none())

    async def get_publishers(self, search: str | None, viewer_id: int | None) -> list[str]:
        query: Select[tuple[str]] = (
            select(distinct(PublisherModel.name)).select_from(BookModel).join(PublisherModel)
        )
        if search is not None:
            query = query.where(PublisherModel.name.ilike(f"%{search}%"))
        query = self._filter_books_by_viewer(query, viewer_id)

        results = await self.session.execute(query)
        return list(results.scalars().all())

    async def get_authors(self, search: str | None, user_id: int | None) -> list[str]:
        query: Select[tuple[str]] = select(distinct(BookModel.authors)).limit(10)
        query = self._filter_books_by_viewer(query, user_id)
        if search is not None:
            query = query.where(BookModel.authors.ilike(f"%{search}%"))
        results = await self.session.execute(query)
        return list(results.scalars().all())

    async def get_book_tags(self, book_id: int) -> list[Tag]:
        query = select(TagModel).join(BookModel.tags).where(BookModel.id == book_id)
        result = await self.session.execute(query)
        return [Tag(id=tag.id, name=tag.name) for tag in result.scalars()]

    @staticmethod
    def _filter_books_by_viewer(query, viewer_id: int | None):
        if viewer_id is not None:
            return query.where(
                BookModel.private.is_(False)
                | (BookModel.private.is_(True) & (BookModel.user_id == viewer_id))
            )
        else:
            return query.where(BookModel.private.is_(False))

    @staticmethod
    def _to_domain(model: BookModel) -> Book:
        return Book(
            id=model.id,
            user_id=model.user_id,
            publisher=Publisher(
                id=model.publisher_id,
                name=model.publisher.name,
            ),
            title=model.title,
            preview_image=model.preview_image,
            file=model.file,
            authors=model.authors,
            description=model.description,
            pages=model.pages,
            size=model.size,
            year=model.year,
            private=model.private,
            language=model.language,
            tags=[tag.name for tag in model.tags],
        )

    @staticmethod
    def _to_model(book: Book) -> BookModel:
        return BookModel(
            id=book.id if book.id else None,
            user_id=book.user_id,
            publisher_id=book.publisher.id,
            title=book.title,
            preview_image=book.preview_image,
            file=book.file,
            authors=book.authors,
            description=book.description,
            pages=book.pages,
            size=book.size,
            year=book.year,
            private=book.private,
            language=book.language,
        )

    async def _get_or_create_publisher(self, publisher_name: str) -> PublisherModel:
        """Находит или создает издательство по названию"""
        query = select(PublisherModel).where(PublisherModel.name.ilike(publisher_name))
        result = await self.session.execute(query)
        result.unique()
        publisher = result.scalar_one_or_none()
        if publisher is None:
            publisher = PublisherModel(name=publisher_name)
            self.session.add(publisher)
            await self.session.flush()
        return publisher

    async def _get_or_create_tags(self, tags: list[str]) -> list[TagModel]:
        """Находит или создает список тегов"""
        model_tags = []
        for tag_name in tags:
            result = await self.session.execute(select(TagModel).where(TagModel.name.ilike(tag_name)))
            result.unique()
            tag = result.scalar_one_or_none()
            if tag is None:
                tag = TagModel(name=tag_name)
            model_tags.append(tag)
        self.session.add_all(model_tags)
        await self.session.flush()

        return model_tags
