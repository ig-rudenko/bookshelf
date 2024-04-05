from fastapi.exceptions import HTTPException

from app.orm.session_manager import db_manager
from app.services.permissions import check_book_owner_permission, check_non_private_or_owner_book_permission
from tests.tests_handlers_books import BaseBookTest


# noinspection PyArgumentList
class TestPermissions(BaseBookTest):

    async def test_check_book_owner_permission(self):
        async with db_manager.session() as session:
            await check_book_owner_permission(session, user_id=self.user_1.id, book=self.book_1)

    async def test_check_book_owner_permission_fail(self):
        async with db_manager.session() as session:
            with self.assertRaises(HTTPException) as context:
                await check_book_owner_permission(session, user_id=self.user_2.id, book=self.book_1)
        self.assertEqual(context.exception.status_code, 403)

    async def test_check_book_owner_permission_invalid_book_id(self):
        async with db_manager.session() as session:
            with self.assertRaises(HTTPException) as context:
                await check_book_owner_permission(session, user_id=self.user_2.id, book=0)
        self.assertEqual(context.exception.status_code, 404)

    async def test_check_book_owner_permission_invalid_user_id(self):
        async with db_manager.session() as session:
            with self.assertRaises(HTTPException) as context:
                await check_book_owner_permission(session, user_id=0, book=self.book_1)
        self.assertEqual(context.exception.status_code, 403)

    async def test_check_non_private_book_permission_with_owner_user(self):
        async with db_manager.session() as session:
            await check_non_private_or_owner_book_permission(
                session, user=self.user_2, book=self.book_private
            )

    async def test_check_non_private_book_permission_no_user_no_private_book(self):
        async with db_manager.session() as session:
            await check_non_private_or_owner_book_permission(session, user=None, book=self.book_1)

    async def test_check_non_private_book_permission_private_book_no_user(self):
        async with db_manager.session() as session:
            with self.assertRaises(HTTPException) as context:
                await check_non_private_or_owner_book_permission(session, user=None, book=self.book_private)
        self.assertEqual(context.exception.status_code, 403)

    async def test_check_non_private_book_permission_private_book_non_owner_user(self):
        async with db_manager.session() as session:
            with self.assertRaises(HTTPException) as context:
                await check_non_private_or_owner_book_permission(
                    session, user=self.user_1, book=self.book_private
                )
        self.assertEqual(context.exception.status_code, 403)

    async def test_check_non_private_book_permission_public_book_no_user(self):
        async with db_manager.session() as session:
            await check_non_private_or_owner_book_permission(session, user=None, book=self.book_1)
