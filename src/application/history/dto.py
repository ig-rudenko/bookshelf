from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, kw_only=True)
class BookReadHistoryDTO:
    id: int
    history: str
    updated_at: datetime
