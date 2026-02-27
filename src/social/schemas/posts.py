import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from social.core.enums import Platform, PostStatus


class PostCreate(BaseModel):
    entity_id: uuid.UUID
    account_id: uuid.UUID | None = None
    platform: Platform
    content: str = Field(min_length=1)
    media_urls: list[str] | None = None
    scheduled_for: datetime | None = None
    source: str | None = None


class PostBulk(BaseModel):
    posts: list[PostCreate]


class PostOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    entity_id: uuid.UUID
    account_id: uuid.UUID | None = None
    platform: Platform
    content: str
    media_urls: list[str] | None = None
    platform_post_id: str | None = None
    platform_post_url: str | None = None
    status: PostStatus
    scheduled_for: datetime | None = None
    posted_at: datetime | None = None
    error: str | None = None
    engagement: dict | None = None
    source: str | None = None
    retry_count: int
    created_at: datetime
    updated_at: datetime
