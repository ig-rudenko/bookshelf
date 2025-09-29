from abc import ABC, abstractmethod


class EmailService(ABC):
    """Сервис для отправки почты"""

    @abstractmethod
    def send_reset_password_email(self, email: str) -> None:
        """Отправка письма для сброса пароля"""
