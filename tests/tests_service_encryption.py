from unittest import TestCase

from app.services.encrypt import validate_password, encrypt_password


class TestServiceEncryption(TestCase):

    def test_password_encryption(self):
        password = "<PASSWORD>"
        enc_password = encrypt_password(password)
        self.assertNotEqual(password, enc_password)
        self.assertTrue(validate_password(password, enc_password))
