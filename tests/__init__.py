import os

from .init import TEST_DB_URL

os.environ.setdefault("DATABASE_URL", TEST_DB_URL)
