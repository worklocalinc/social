import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from social.core.enums import EntityType


class EntityCreate(BaseModel):
    slug: str = Field(max_length=255)
    type: EntityType
    name: str = Field(max_length=255)
    metadata: dict | None = None


class EntityUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    type: EntityType | None = None
    metadata: dict | None = None


class EntityOut(BaseModel):
    model_config = {"from_attributes": True, "populate_by_name": True}

    id: uuid.UUID
    slug: str
    type: EntityType
    name: str
    metadata: dict | None = Field(default=None, validation_alias="metadata_")
    created_at: datetime
    updated_at: datetime
