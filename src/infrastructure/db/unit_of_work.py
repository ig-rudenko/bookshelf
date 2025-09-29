from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.books.repository import BookRepository
from src.domain.bookshelves.repository import BookshelfRepository
from src.domain.comments.repository import CommentRepository
from src.domain.common.unit_of_work import UnitOfWork
from src.domain.history.repository import BookReadHistoryRepository
from src.domain.users.repository import UserRepository
from src.infrastructure.db.repositories.books_repo import SqlAlchemyBookRepository
from src.infrastructure.db.repositories.bookshelves_repo import SqlAlchemyBookshelfRepository
from src.infrastructure.db.repositories.comments_repo import SqlAlchemyCommentRepository
from src.infrastructure.db.repositories.history_repo import SqlAlchemyBookReadHistoryRepositoryRepository
from src.infrastructure.db.repositories.refresh_token_repo import SqlAlchemyRefreshTokenRepository
from src.infrastructure.db.repositories.users_repo import SqlAlchemyUserRepository


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session: AsyncSession):
        self._session = session
        self._books: SqlAlchemyBookRepository | None = None
        self._refresh_token: SqlAlchemyRefreshTokenRepository | None = None
        self._users: SqlAlchemyUserRepository | None = None
        self._bookshelves: SqlAlchemyBookshelfRepository | None = None
        self._comments: SqlAlchemyCommentRepository | None = None
        self._book_read_history: SqlAlchemyBookReadHistoryRepositoryRepository | None = None

    @property
    def books(self) -> BookRepository:
        if self._books is None:
            self._books = SqlAlchemyBookRepository(self._session)
        return self._books

    @property
    def bookshelves(self) -> BookshelfRepository:
        if self._bookshelves is None:
            self._bookshelves = SqlAlchemyBookshelfRepository(self._session)
        return self._bookshelves

    @property
    def comments(self) -> CommentRepository:
        if self._comments is None:
            self._comments = SqlAlchemyCommentRepository(self._session)
        return self._comments

    @property
    def book_read_history(self) -> BookReadHistoryRepository:
        if self._book_read_history is None:
            self._book_read_history = SqlAlchemyBookReadHistoryRepositoryRepository(self._session)
        return self._book_read_history

    @property
    def users(self) -> UserRepository:
        if self._users is None:
            self._users = SqlAlchemyUserRepository(self._session)
        return self._users

    @property
    def session(self) -> AsyncSession:
        return self._session

    @property
    def refresh_token(self) -> SqlAlchemyRefreshTokenRepository:
        if self._refresh_token is None:
            self._refresh_token = SqlAlchemyRefreshTokenRepository(self._session)
        return self._refresh_token

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()
