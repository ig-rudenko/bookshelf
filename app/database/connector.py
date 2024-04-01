from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine


class AsyncConnection:

    def __init__(self):
        self._engine = None
        self._session = None

    def initialize(self, dsn: str, echo: bool = False):
        """Например: 'sqlite+aiosqlite:///db.sqlite3'"""
        self._engine = create_async_engine(dsn, echo=echo)
        self._session = AsyncSession(self._engine)

    @property
    def session(self) -> AsyncSession:
        return self._session


db_conn = AsyncConnection()
