from dataclasses import dataclass
from typing import Literal


@dataclass(slots=True, kw_only=True)
class UserFilterDTO:
    sort_by: str
    sort_order: Literal["asc", "desc"]
    page: int
    per_page: int
