import pathlib

test_db_path = pathlib.Path(__file__).parent.parent / "test.db"
TEST_DB_URL = f"sqlite+aiosqlite:///{test_db_path}"
