from pydantic import BaseModel
from typing import List, Optional


class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None


class ChatEvent(BaseModel):
    type: str
    content: str


class SourceRequest(BaseModel):
    name: str
    base_url: str
    crawler_type: str


class WikiState(BaseModel):
    symbol: str
    wiki_data: dict
    version: int
