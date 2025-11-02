from asyncio import current_task
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)


class DatabaseSessionManager:
    """
    Менеджер сессий базы данных с поддержкой асинхронности.

    Класс предоставляет методы для инициализации,
    закрытия соединения с базой данных, а также создания
    асинхронных сессий и подключений.
    """

    def __init__(self) -> None:
        self._engine: AsyncEngine | None = None
        self._session_maker: async_sessionmaker[AsyncSession] | None = None

    def init(self, dsn: str, *, echo: bool, pool_size: int, max_overflow: int) -> None:
        """Инициализирует соединение с базой данных."""
        self._engine = create_async_engine(
            url=dsn,
            echo=echo,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )
        self._session_maker = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

    @property
    def session_maker(self) -> async_sessionmaker[AsyncSession] | None:
        return self._session_maker

    async def close(self) -> None:
        """Закрывает соединение с базой данных."""

        if self._engine is None:
            return
        await self._engine.dispose()
        self._engine = None
        self._session_maker = None

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """
        Контекстный менеджер для создания асинхронной сессии.

        В качестве контекста возвращает объект `AsyncSession`.
        В случае возникновения исключения внутри контекста,
        откатывает транзакцию.
        """
        if self._session_maker is None:
            raise OSError("DatabaseSessionManager is not initialized")
        async with self._session_maker() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    @asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        """
        Контекстный менеджер для создания асинхронного подключения.

        В качестве контекста возвращает объект `AsyncConnection`.
        В случае возникновения исключения внутри контекста,
        откатывает транзакцию.
        """
        if self._engine is None:
            raise OSError("DatabaseSessionManager is not initialized")
        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise


db_manager: DatabaseSessionManager = DatabaseSessionManager()


@asynccontextmanager
async def scoped_session():
    scoped_factory = async_scoped_session(
        db_manager.session_maker,
        scopefunc=current_task,
    )
    try:
        async with scoped_factory() as s:
            yield s
            await s.commit()
    finally:
        await scoped_factory.remove()
