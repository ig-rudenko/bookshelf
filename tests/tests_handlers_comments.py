from fastapi.exceptions import HTTPException
from fastapi.testclient import TestClient

from app.handlers.comments import router
from app.orm.session_manager import db_manager
from app.services.auth import create_jwt_token_pair
from tests import TEST_DB_URL
from tests.tests_handlers_books import BaseBookTest


class TestComments(BaseBookTest):

    @classmethod
    def setUpClass(cls):
        db_manager.init(TEST_DB_URL)
        cls.client = TestClient(router)

    async def test_create_comment(self):
        token_pair = create_jwt_token_pair(user_id=self.user_1.id)
        response = self.client.post(
            f"/comments/book/{self.book_1.id}",
            headers={"Authorization": f"Bearer {token_pair.access_token}"},
            json={"text": "test comment"},
        )
        self.assertEqual(response.status_code, 201)
        self.assertListEqual(
            ["id", "text", "createdAt", "user"],
            list(response.json().keys()),
        )

    async def test_create_comment_no_auth(self):
        with self.assertRaises(HTTPException) as context:
            self.client.post(
                f"/comments/book/{self.book_1.id}",
                json={"text": "test comment"},
            )
        self.assertEqual(context.exception.status_code, 401)

    async def test_create_comment_invalid_book(self):
        token_pair = create_jwt_token_pair(user_id=self.user_1.id)
        with self.assertRaises(HTTPException) as context:
            self.client.post(
                f"/comments/book/0",
                headers={"Authorization": f"Bearer {token_pair.access_token}"},
                json={"text": "test comment"},
            )
        self.assertEqual(context.exception.status_code, 404)

    async def test_create_update_comment(self):
        token_pair = create_jwt_token_pair(user_id=self.user_1.id)
        response = self.client.post(
            f"/comments/book/{self.book_1.id}",
            headers={"Authorization": f"Bearer {token_pair.access_token}"},
            json={"text": "test comment"},
        )

        response = self.client.put(
            f"/comments/{response.json()['id']}",
            headers={"Authorization": f"Bearer {token_pair.access_token}"},
            json={"text": "test comment updated"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertListEqual(
            ["id", "text", "createdAt", "bookId"],
            list(data.keys()),
        )
        self.assertEqual(data["text"], "test comment updated")

    async def test_update_comment_no_auth(self):
        token_pair = create_jwt_token_pair(user_id=self.user_1.id)
        response = self.client.post(
            f"/comments/book/{self.book_1.id}",
            headers={"Authorization": f"Bearer {token_pair.access_token}"},
            json={"text": "test comment"},
        )
        with self.assertRaises(HTTPException) as context:
            self.client.put(
                f"/comments/{response.json()['id']}",
                json={"text": "test comment updated"},
            )
        self.assertEqual(context.exception.status_code, 401)

    async def test_delete_comment(self):
        token_pair = create_jwt_token_pair(user_id=self.user_1.id)
        response = self.client.post(
            f"/comments/book/{self.book_1.id}",
            headers={"Authorization": f"Bearer {token_pair.access_token}"},
            json={"text": "test comment"},
        )
        response = self.client.delete(
            f"/comments/{response.json()['id']}",
            headers={"Authorization": f"Bearer {token_pair.access_token}"},
        )
        self.assertEqual(response.status_code, 204)

    async def test_delete_comment_no_auth(self):
        token_pair = create_jwt_token_pair(user_id=self.user_1.id)
        response = self.client.post(
            f"/comments/book/{self.book_1.id}",
            headers={"Authorization": f"Bearer {token_pair.access_token}"},
            json={"text": "test comment"},
        )
        with self.assertRaises(HTTPException) as context:
            self.client.delete(
                f"/comments/{response.json()['id']}",
            )
        self.assertEqual(context.exception.status_code, 401)
