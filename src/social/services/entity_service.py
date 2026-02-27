import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from social.core.enums import EntityType
from social.core.exceptions import Conflict, NotFound
from social.db.models import Entity
from social.schemas.entities import EntityCreate, EntityUpdate


async def create_entity(db: AsyncSession, data: EntityCreate) -> Entity:
    existing = await db.execute(select(Entity).where(Entity.slug == data.slug, Entity.deleted_at.is_(None)))
    if existing.scalar_one_or_none():
        raise Conflict(f"Entity with slug '{data.slug}' already exists")

    entity = Entity(
        slug=data.slug,
        type=data.type,
        name=data.name,
        metadata_=data.metadata,
    )
    db.add(entity)
    await db.flush()
    await db.refresh(entity)
    return entity


async def get_entity(db: AsyncSession, entity_id: uuid.UUID) -> Entity:
    result = await db.execute(select(Entity).where(Entity.id == entity_id, Entity.deleted_at.is_(None)))
    entity = result.scalar_one_or_none()
    if not entity:
        raise NotFound("Entity not found")
    return entity


async def list_entities(
    db: AsyncSession, entity_type: EntityType | None = None, limit: int = 100, offset: int = 0
) -> list[Entity]:
    q = select(Entity).where(Entity.deleted_at.is_(None))
    if entity_type:
        q = q.where(Entity.type == entity_type)
    q = q.order_by(Entity.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(q)
    return list(result.scalars().all())


async def update_entity(db: AsyncSession, entity_id: uuid.UUID, data: EntityUpdate) -> Entity:
    entity = await get_entity(db, entity_id)
    update_data = data.model_dump(exclude_unset=True)
    if "metadata" in update_data:
        update_data["metadata_"] = update_data.pop("metadata")
    for field, value in update_data.items():
        setattr(entity, field, value)
    await db.flush()
    await db.refresh(entity)
    return entity


async def delete_entity(db: AsyncSession, entity_id: uuid.UUID) -> Entity:
    entity = await get_entity(db, entity_id)
    entity.deleted_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(entity)
    return entity
