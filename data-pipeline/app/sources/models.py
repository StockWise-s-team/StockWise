from dataclasses import dataclass
from uuid import UUID
from typing import Optional

@dataclass
class NewsSource:
    id: Optional[UUID]
    name: str
    base_url: str
    crawler_type: str
    is_active: bool = True
