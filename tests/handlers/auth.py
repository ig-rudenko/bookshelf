from unittest import IsolatedAsyncioTestCase

from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.testclient import TestClient
from sqlalchemy.sql.expression import delete

from app.database.connector import db_conn
from app.handlers.auth import router
from app.models import User
from app.services.auth import create_jwt_token_pair


class RegisterUserTest(IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(router)

    async def asyncTearDown(self):
        async with db_conn.session as conn:
            await conn.execute(delete(User))
            await conn.commit()

    async def test_create_user(self):
        user_data = {"username": "testuser", "password": "testpassword", "email": "igor@mail.com"}
        response = self.client.post("/auth/users", json=user_data)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            response.json(),
            {
                "username": "testuser",
                "email": "igor@mail.com",
                "first_name": None,
                "last_name": None,
            },
        )
        user = await User.get(username="testuser")
        self.assertEqual(user.email, "igor@mail.com")

    def test_register_user_duplicate(self):
        """Попытка зарегистрировать уже существующего пользователя"""
        user_data = {"username": "testuser", "password": "testpassword", "email": "igor@mail.com"}
        self.client.post("/auth/users", json=user_data)
        with self.assertRaises(HTTPException):
            self.client.post("/auth/users", json=user_data)

    def test_create_user_empty_password(self):
        """Пустой пароль"""
        with self.assertRaises(RequestValidationError):
            self.client.post(
                "/auth/users", json={"username": "testuser", "password": "", "email": "igor@mail.com"}
            )

    def test_create_user_empty_data(self):
        """Пустой пароль"""
        with self.assertRaises(RequestValidationError):
            self.client.post("/auth/users")

    def test_create_user_without_email(self):
        """Пустой пароль"""
        with self.assertRaises(RequestValidationError):
            self.client.post("/auth/users", json={"username": "testuser", "password": "password"})


class AuthJWTTest(IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(router)

    async def asyncSetUp(self):
        self.user_data = {"username": "testuser", "password": "testpassword", "email": "igor@mail.com"}
        self.client.post("/auth/users", json=self.user_data)

    async def asyncTearDown(self):
        async with db_conn.session as conn:
            await conn.execute(delete(User))
            await conn.commit()

    def test_get_tokens(self):
        """Тест на успешное получение токенов JWT"""
        response = self.client.post("/auth/token", json=self.user_data)
        self.assertEqual(response.status_code, 200)
        tokens = response.json()
        self.assertIn("accessToken", tokens)
        self.assertIn("refreshToken", tokens)

    def test_get_tokens_invalid_credentials(self):
        # Тест на попытку получить токены JWT с неверными учетными данными
        user_credentials = {"username": "testuser", "password": "wrongpassword"}
        with self.assertRaises(HTTPException):
            self.client.post("/auth/token", json=user_credentials)

    async def test_verify_jwt(self):
        """Тест на успешное верифицирование JWT"""
        user = await User.get(username="testuser")
        token_pair = create_jwt_token_pair(user_id=user.id)

        response = self.client.get(
            "/auth/myself", headers={"Authorization": f"Bearer {token_pair.access_token}"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["username"], user.username)
        self.assertEqual(data.get("password"), None)
        self.assertEqual(data["email"], user.email)

    async def test_refresh_jwt(self):
        user = await User.get(username="testuser")
        token_pair = create_jwt_token_pair(user_id=user.id)
        response = self.client.post("/auth/token/refresh", json={"refreshToken": token_pair.refresh_token})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("accessToken", data)
        self.assertNotIn("refreshToken", data)
