from fastapi.exceptions import HTTPException
from fastapi.testclient import TestClient

from app.handlers.bookmarks import router as bookmarks_router
from app.models import Book
from app.orm.session_manager import db_manager
from app.schemas.books import BookSchema
from app.services.aaa import create_jwt_token_pair
from tests import TEST_DB_URL
from tests_handlers_books import BaseBookTest


# noinspection PyArgumentList
class TestFavoriteBooks(BaseBookTest):

    @classmethod
    def setUpClass(cls):
        db_manager.init(TEST_DB_URL)
        cls.client = TestClient(bookmarks_router)

    async def test_mark_favorite(self):
        token_pair = create_jwt_token_pair(user_id=self.user_1.id)
        response = self.client.post(
            f"/bookmarks/{self.book_1.id}/favorite",
            headers={"Authorization": f"Bearer {token_pair.access_token}"},
        )
        self.assertEqual(response.status_code, 200)

        async with db_manager.session() as session:
            book = await Book.get(session, id=self.book_1.id)
            favorite_for_users = list(await book.await_attr.favorite_for_users)

        self.assertEqual(len(favorite_for_users), 1)
        self.assertEqual(favorite_for_users[0].id, self.user_1.id)

    async def test_mark_favorite_no_auth(self):
        with self.assertRaises(HTTPException) as context:
            self.client.post(f"/bookmarks/{self.book_1.id}/favorite")
        self.assertEqual(context.exception.status_code, 401)

    async def test_mark_favorite_invalid_book(self):
        token_pair = create_jwt_token_pair(user_id=self.user_1.id)
        with self.assertRaises(HTTPException) as context:
            self.client.post(
                f"/bookmarks/0/favorite",
                headers={"Authorization": f"Bearer {token_pair.access_token}"},
            )
        self.assertEqual(context.exception.status_code, 404)

    async def test_unmark_favorite(self):
        token_pair = create_jwt_token_pair(user_id=self.user_1.id)
        self.client.post(
            f"/bookmarks/{self.book_1.id}/favorite",
            headers={"Authorization": f"Bearer {token_pair.access_token}"},
        )
        response = self.client.delete(
            f"/bookmarks/{self.book_1.id}/favorite",
            headers={"Authorization": f"Bearer {token_pair.access_token}"},
        )
        self.assertEqual(response.status_code, 204)

        async with db_manager.session() as session:
            book = await Book.get(session, id=self.book_1.id)
            favorite_for_users = list(await book.await_attr.favorite_for_users)

        self.assertEqual(len(favorite_for_users), 0)

    async def test_favorites_list(self):
        token_pair = create_jwt_token_pair(user_id=self.user_1.id)
        self.client.post(
            f"/bookmarks/{self.book_1.id}/favorite",
            headers={"Authorization": f"Bearer {token_pair.access_token}"},
        )

        response = self.client.get(
            f"/bookmarks/favorite",
            headers={"Authorization": f"Bearer {token_pair.access_token}"},
        )
        self.assertEqual(response.status_code, 200)
        valid = {
            "books": [BookSchema.model_validate(self.book_1).model_dump(by_alias=True)],
            "currentPage": 1,
            "maxPages": 1,
            "perPage": 25,
            "totalCount": 1,
        }
        self.assertEqual(valid, response.json())


# noinspection PyArgumentList
class TestReadBooks(BaseBookTest):

    @classmethod
    def setUpClass(cls):
        db_manager.init(TEST_DB_URL)
        cls.client = TestClient(bookmarks_router)

    async def test_mark_read(self):
        token_pair = create_jwt_token_pair(user_id=self.user_1.id)
        response = self.client.post(
            f"/bookmarks/{self.book_1.id}/read",
            headers={"Authorization": f"Bearer {token_pair.access_token}"},
        )
        self.assertEqual(response.status_code, 200)

        async with db_manager.session() as session:
            book = await Book.get(session, id=self.book_1.id)
            read_by_users = list(await book.await_attr.read_by_users)

        self.assertEqual(len(read_by_users), 1)
        self.assertEqual(read_by_users[0].id, self.user_1.id)

    async def test_mark_read_no_auth(self):
        with self.assertRaises(HTTPException) as context:
            self.client.post(f"/bookmarks/{self.book_1.id}/read")
        self.assertEqual(context.exception.status_code, 401)

    async def test_mark_read_invalid_book(self):
        token_pair = create_jwt_token_pair(user_id=self.user_1.id)
        with self.assertRaises(HTTPException) as context:
            self.client.post(
                f"/bookmarks/0/read",
                headers={"Authorization": f"Bearer {token_pair.access_token}"},
            )
        self.assertEqual(context.exception.status_code, 404)

    async def test_unmark_read(self):
        token_pair = create_jwt_token_pair(user_id=self.user_1.id)
        self.client.post(
            f"/bookmarks/{self.book_1.id}/read",
            headers={"Authorization": f"Bearer {token_pair.access_token}"},
        )
        response = self.client.delete(
            f"/bookmarks/{self.book_1.id}/read",
            headers={"Authorization": f"Bearer {token_pair.access_token}"},
        )
        self.assertEqual(response.status_code, 204)

        async with db_manager.session() as session:
            book = await Book.get(session, id=self.book_1.id)
            read_by_users = list(await book.await_attr.read_by_users)

        self.assertEqual(len(read_by_users), 0)

    async def test_read_list(self):
        token_pair = create_jwt_token_pair(user_id=self.user_1.id)
        self.client.post(
            f"/bookmarks/{self.book_1.id}/read",
            headers={"Authorization": f"Bearer {token_pair.access_token}"},
        )

        response = self.client.get(
            f"/bookmarks/read",
            headers={"Authorization": f"Bearer {token_pair.access_token}"},
        )
        self.assertEqual(response.status_code, 200)
        valid = {
            "books": [BookSchema.model_validate(self.book_1).model_dump(by_alias=True)],
            "currentPage": 1,
            "maxPages": 1,
            "perPage": 25,
            "totalCount": 1,
        }
        self.assertEqual(valid, response.json())
