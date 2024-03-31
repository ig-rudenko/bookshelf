import pathlib

from app.database.connector import db_conn

test_db = pathlib.Path(__file__).parent.parent / "test.db"
db_conn.initialize(f"sqlite+aiosqlite:///{test_db}")
