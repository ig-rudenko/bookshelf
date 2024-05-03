import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.services.deco import singleton
from app.settings import settings


@singleton
class EmailService:
    """Сервис для отправки почты"""

    def __init__(self):
        self._from = settings.EMAIL_FROM
        self._password = settings.EMAIL_PASSWORD
        self._smtp_server = "smtp.yandex.ru"
        self._smtp_port = 465

    def _create_message(self, email: str, subject, body) -> str:
        message = MIMEMultipart()
        message["From"] = self._from
        message["To"] = email
        message["Subject"] = subject
        message.attach(MIMEText(body, "html"))
        return message.as_string()

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

    def send_reset_password_email(self, email: str, subject: str, context: dict) -> None:
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


def get_email_service() -> EmailService:
    """Получение сервиса для отправки почты"""
    return EmailService()
