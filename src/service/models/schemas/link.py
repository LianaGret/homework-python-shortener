from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, HttpUrl, field_validator


class LinkBase(BaseModel):
    original_url: HttpUrl


class LinkCreate(LinkBase):
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime] = None

    @field_validator("custom_alias")
    def validate_custom_alias(cls, v):
        if v is not None:
            if len(v) < 3 or len(v) > 16:
                raise ValueError("Custom alias must be between 3 and 16 characters")
            if not v.isalnum():
                raise ValueError("Custom alias must contain only alphanumeric characters")
        return v


class LinkUpdate(BaseModel):
    original_url: HttpUrl
    expires_at: Optional[datetime] = None


class LinkResponse(BaseModel):
    short_code: str
    original_url: HttpUrl
    created_at: datetime
    expires_at: Optional[datetime] = None
    custom_alias: bool


class LinkStats(BaseModel):
    short_code: str
    original_url: HttpUrl
    created_at: datetime
    visit_count: int
    last_visited_at: Optional[datetime] = None


class LinkSearchResponse(BaseModel):
    original_url: HttpUrl
    links: List[LinkResponse]
