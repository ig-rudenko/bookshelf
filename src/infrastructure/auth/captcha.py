import aiohttp

from app.settings import settings


async def verify_captcha(captcha_token: str, remote_ip: str) -> bool:
    """
    Проверяет капчу, если включена настройка.
    :param captcha_token: Токен капчи.
    :param remote_ip: IP адрес, который отправил капчу.
    :param secret: Секретный ключ для проверки капчи.
    :return:
    """
    if not settings.RECAPTCHA_ENABLED:
        return True

    async with aiohttp.ClientSession() as session, session.post(
        "https://www.google.com/recaptcha/api/siteverify",
        data={
            "secret": settings.RECAPTCHA_SECRET_KEY,
            "response": captcha_token,
            "remoteip": remote_ip,
        },
    ) as response:
        try:
            data = await response.json()
        except ValueError:
            return False
        else:
            return data.get("success", False)
