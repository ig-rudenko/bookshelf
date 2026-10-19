import json
import unittest
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.application.books.handlers import BookmarksQueryHandler, BookQueryHandler
from src.domain.books.entities import BookFilter, BookmarksQueryFilter
from src.infrastructure.db.base_model import OrmBase
from src.infrastructure.db.models import (
    BookHistoryModel, BookModel, FavoriteBookModel, PublisherModel, ReadBookModel, TagModel, UserModel,
)
from src.infrastructure.db.repositories.books_repo import SqlAlchemyBookRepository
from src.infrastructure.db.repositories.history_repo import SqlAlchemyBookReadHistoryRepositoryRepository
from src.presentation.api.auth import get_current_user, superuser_required
from src.presentation.api.dependencies import get_book_query_handler, get_bookmark_query_handler
from src.presentation.api.handlers import books, bookmarks
from src.presentation.api.handlers.admin import users


class LibraryFiltersTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.engine = create_async_engine('sqlite+aiosqlite:///:memory:')
        async with self.engine.begin() as connection:
            await connection.run_sync(OrmBase.metadata.create_all)
        self.session = async_sessionmaker(self.engine, expire_on_commit=False)()
        self.session.add_all([UserModel(id=i, username=f'user{i}', password='unused') for i in (1, 2, 3)])
        self.session.add_all([PublisherModel(id=1, name='Technical Press'), PublisherModel(id=2, name='Other Press')])
        sql, db, python = (TagModel(id=i, name=name) for i, name in enumerate(('SQL', 'Databases', 'Python'), 1))
        self.session.add_all([sql, db, python])
        for i in range(1, 7):
            self.session.add(BookModel(
                id=i, user_id=2 if i in (4, 5) else 1, publisher_id=2 if i == 2 else 1,
                title='Python notes' if i == 2 else f'SQL book {i}', authors='Ada' if i in (1, 3) else 'Grace',
                preview_image=f'{i}.png', file=f'{i}.pdf', description='Technical reference', pages=i * 100 + 20,
                size=100, year=2020 + i, private=i in (4, 6), language='English' if i == 2 else 'Русский',
                tags=[python, db] if i == 2 else [sql, db],
            ))
            if i != 5:
                self.session.add(FavoriteBookModel(id=i, book_id=i, user_id=1))
                self.session.add(ReadBookModel(id=i, book_id=i, user_id=1))
            self.session.add(BookHistoryModel(
                id=i, book_id=i, user_id=1, pdf_history_updated_at=datetime(2026, 1, 1, tzinfo=UTC) + timedelta(days=i),
                pdf_history=json.dumps({'files': [{'fingerprint': str(i), 'sidebarView': 0, 'page': i * 10,
                    'zoom': 'auto', 'scrollLeft': 0, 'scrollTop': 0, 'rotation': 0}]}),
            ))
        self.session.add(FavoriteBookModel(id=9, book_id=5, user_id=2))
        self.session.add(ReadBookModel(id=9, book_id=5, user_id=2))
        await self.session.commit()
        self.books = SqlAlchemyBookRepository(self.session)
        histories = SqlAlchemyBookReadHistoryRepositoryRepository(self.session)

        class TestUow:
            async def __aenter__(inner):
                return inner

            async def __aexit__(inner, *_):
                pass

        uow = TestUow()
        uow.books, uow.book_read_history = self.books, histories
        self.handler = BookQueryHandler(uow, SimpleNamespace(get_media_url=AsyncMock(side_effect=lambda path: path)), None)

    async def asyncTearDown(self):
        await self.session.close()
        await self.engine.dispose()

    async def test_bookmarks_filter_before_pagination_and_keep_user_scope(self):
        for method in (self.books.get_favorite_books, self.books.get_read_books):
            for page, expected in ((1, [6]), (2, [3]), (3, [1])):
                with self.subTest(method=method.__name__, page=page):
                    books, count = await method(BookmarksQueryFilter(
                        user_id=1, page=page, page_size=1, book_filter=BookFilter(tags=['sql', 'Databases']),
                    ))
                    self.assertEqual([book.id for book in books], expected)
                    self.assertEqual(count, 3)

    async def test_bookmarks_combine_filters_and_report_no_matches(self):
        for method in (self.books.get_favorite_books, self.books.get_read_books):
            books, count = await method(BookmarksQueryFilter(user_id=1, page=1, page_size=25, book_filter=BookFilter(
                authors='Ada', publisher='Technical', language='Русский', pages_gt=200, pages_lt=400,
            )))
            self.assertEqual(([book.id for book in books], count), ([3], 1))
            books, count = await method(BookmarksQueryFilter(user_id=1, page=1, page_size=25,
                book_filter=BookFilter(tags=['SQL', 'Python'])))
            self.assertEqual((books, count), ([], 0))

    async def test_history_filters_once_and_preserves_order_and_progress(self):
        for page, expected in ((1, [6, 5]), (2, [3, 1])):
            books, count = await self.handler.handler_get_last_viewed_books(1, page, 2, BookFilter(tags=['SQL']))
            self.assertEqual([book.id for book in books], expected)
            self.assertEqual([book.read_pages for book in books], [i * 10 for i in expected])
            self.assertEqual(count, 4)

    async def test_empty_history_and_no_matches_stay_empty(self):
        for user_id, filter_ in ((3, BookFilter()), (1, BookFilter(search='missing book'))):
            books, count = await self.handler.handler_get_last_viewed_books(user_id, 1, 25, filter_)
            self.assertEqual((books, count), ([], 0))

    async def test_duplicate_history_keeps_latest_progress_and_counts_books(self):
        self.session.add(BookHistoryModel(
            id=10, book_id=6, user_id=1, pdf_history_updated_at=datetime(2026, 2, 1, tzinfo=UTC),
            pdf_history=json.dumps({'files': [{'fingerprint': '6', 'sidebarView': 0, 'page': 99,
                'zoom': 'auto', 'scrollLeft': 0, 'scrollTop': 0, 'rotation': 0}]}),
        ))
        await self.session.commit()
        for page, expected, progress in ((1, [6, 5, 3], [99, 50, 30]), (2, [1], [10])):
            books, count = await self.handler.handler_get_last_viewed_books(1, page, 3, BookFilter(tags=['SQL']))
            self.assertEqual([book.id for book in books], expected)
            self.assertEqual([book.read_pages for book in books], progress)
            self.assertEqual(count, 4)

    def api_app(self):
        app = FastAPI()
        app.include_router(books.router)
        app.include_router(bookmarks.router)
        app.include_router(users.router, prefix='/admin')
        app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=1, is_superuser=True)
        app.dependency_overrides[superuser_required] = lambda: None
        app.dependency_overrides[get_book_query_handler] = lambda: self.handler
        app.dependency_overrides[get_bookmark_query_handler] = lambda: BookmarksQueryHandler(
            self.handler.uow, self.handler.storage,
        )
        return app

    async def test_api_filters_and_validation_for_personal_and_admin_lists(self):
        async with AsyncClient(transport=ASGITransport(app=self.api_app()), base_url='http://test') as client:
            for endpoint in ('/bookmarks/favorite', '/bookmarks/read', '/books/last-viewed',
                             '/admin/users/1/favorite', '/admin/users/1/read', '/admin/users/1/last-viewed'):
                with self.subTest(endpoint=endpoint):
                    result = await client.get(endpoint, params=[('authors', 'Ada'), ('tags', 'SQL'),
                        ('tags', 'Databases'), ('pages-gt', '200'), ('pages-lt', '400'), ('per-page', '1')])
                    self.assertEqual(result.status_code, 200, result.text)
                    payload = result.json()
                    self.assertEqual(payload['totalCount'], 1)
                    self.assertEqual(payload['perPage'], 1)
                    self.assertEqual([book['id'] for book in payload['books']], [3])
                    invalid = await client.get(endpoint, params={'pages-gt': 400, 'pages-lt': 200})
                    self.assertEqual(invalid.status_code, 422)

    async def test_search_by_author_and_topic_and_client_cannot_change_owner(self):
        async with AsyncClient(transport=ASGITransport(app=self.api_app()), base_url='http://test') as client:
            for endpoint in ('/bookmarks/favorite', '/bookmarks/read'):
                by_author = await client.get(endpoint, params={'search': 'Ada', 'favorite_by': 2, 'read_by': 2})
                self.assertEqual([book['id'] for book in by_author.json()['books']], [3, 1])
                by_topic = await client.get(endpoint, params={'search': 'Databases'})
                self.assertEqual(by_topic.json()['totalCount'], 4)
