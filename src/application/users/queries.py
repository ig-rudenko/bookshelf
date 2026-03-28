from dataclasses import dataclass
from typing import Literal


@dataclass(slots=True, kw_only=True)
class UserFilterDTO:
    search: str
    sort_by: str
    sort_order: Literal["asc", "desc"]
    page: int
    per_page: int
