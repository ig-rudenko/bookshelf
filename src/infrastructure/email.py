import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.application.services.email import EmailService
from src.infrastructure.auth.token_service import create_reset_password_token
from src.infrastructure.settings import settings


class SMTPEmailService(EmailService):
    """Сервис для отправки почты"""

    def __init__(self, email_from: str, email_password: str, smtp_server: str, smtp_port: int) -> None:
        self._from = email_from
        self._password = email_password
        self._smtp_server = smtp_server
        self._smtp_port = smtp_port

    def send_reset_password_email(self, email: str) -> None:
        """
        Отправляет письмо на смену пароля.
        :param email: Email пользователя.
        """

        secret_token = create_reset_password_token(email=email)
        forget_url_link = f"https://it-bookshelf.ru/reset-password/{secret_token}"

        email_body = {
            "link_expire_minutes": settings.FORGET_PASSWORD_LINK_EXPIRE_MINUTES,
            "reset_link": forget_url_link,
        }
        subject = "Сброс пароля на сайте it-bookshelf.ru"
        self._send_reset_password_email(email=email, subject=subject, context=email_body)

    def _create_message(self, email: str, subject, body) -> str:
        message = MIMEMultipart()
        message["From"] = self._from
        message["To"] = email
        message["Subject"] = subject
        message.attach(MIMEText(body, "html"))
        return message.as_string()

    def _send_reset_password_email(self, email: str, subject: str, context: dict) -> None:
        """Отправка письма для сброса пароля"""
        try:
            server = smtplib.SMTP_SSL(self._smtp_server, self._smtp_port, timeout=10)
            try:
                server.login(self._from, self._password)
                message = self._create_message(
                    email,
                    subject,
                    self._render_reset_body(context),
                )
                server.sendmail(from_addr=self._from, to_addrs=[email], msg=message)
            finally:
                server.quit()
        except Exception as e:
            print(e)

    @staticmethod
    def _render_reset_body(context: dict) -> str:
        """Рендер тела письма для сброса пароля"""
        return """
            <h3>Сброс пароля для сайта it-bookshelf.ru</h3>
            <div>
                <a href="{reset_link}" target="_blank">Ссылка будет доступна в течение {link_expire_minutes} минут.</a>
            </div>
    """.format(
            **context
        )
