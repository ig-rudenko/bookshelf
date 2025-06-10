from app.settings import settings


def get_media_url(file: str):
    if file.startswith("/media"):
        file = file[6:]
    elif file.startswith("media"):
        file = file[5:]
    if not file.startswith("/"):
        file = "/" + file

    if not settings.media_url.startswith("http") and not settings.media_url.startswith("/"):
        settings.media_url = "/" + settings.media_url

    if settings.media_url.endswith("/"):
        return settings.media_url[:-1] + file

    return settings.media_url + file
