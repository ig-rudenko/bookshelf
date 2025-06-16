import os

from .init import TEST_DB_URL, TEST_MEDIA_PATH, TEST_MEDIA_URL

os.environ.setdefault("DATABASE_URL", TEST_DB_URL)
os.environ.setdefault("MEDIA_ROOT", TEST_MEDIA_PATH.absolute().as_posix())
os.environ.setdefault("MEDIA_URL", TEST_MEDIA_URL)
