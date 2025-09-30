from dataclasses import dataclass


@dataclass(slots=True, kw_only=True)
class SetReadBookHistory:
    book_id: int
    user_id: int
    history: str
