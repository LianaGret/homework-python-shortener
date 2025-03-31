from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Link:
    id: int
    short_code: str
    original_url: str
    custom_alias: bool
    created_at: datetime
    expires_at: Optional[datetime] = None
