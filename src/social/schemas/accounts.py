import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from social.core.enums import AccountStatus, Platform


class AccountCreate(BaseModel):
    entity_id: uuid.UUID
    platform: Platform
    platform_user_id: str | None = None
    handle: str | None = Field(default=None, max_length=255)
    credentials: dict | None = None
    metadata: dict | None = None


class AccountUpdate(BaseModel):
    handle: str | None = Field(default=None, max_length=255)
    credentials: dict | None = None
    status: AccountStatus | None = None
    metadata: dict | None = None


class AccountOut(BaseModel):
    model_config = {"from_attributes": True, "populate_by_name": True}

    id: uuid.UUID
    entity_id: uuid.UUID
    platform: Platform
    platform_user_id: str | None = None
    handle: str | None = None
    status: AccountStatus
    rate_limit_remaining: int | None = None
    rate_limit_reset: datetime | None = None
    metadata: dict | None = Field(default=None, validation_alias="metadata_")
    created_at: datetime
    updated_at: datetime
