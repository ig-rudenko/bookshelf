import os
import pathlib

tests_path = pathlib.Path(__file__).parent
TEST_MEDIA_PATH = tests_path / "media-test"

test_db_path = tests_path.parent / "test.db"
TEST_DB_URL = os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{test_db_path}")
