import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from social.api.deps import Principal, get_principal
from social.core.enums import EntityType
from social.db.deps import get_db
from social.schemas.entities import EntityCreate, EntityOut, EntityUpdate
from social.services import entity_service

router = APIRouter(prefix="/entities", tags=["entities"])


@router.post("", response_model=EntityOut, status_code=201)
async def create_entity(
    data: EntityCreate,
    db: AsyncSession = Depends(get_db),
    _: Principal = Depends(get_principal),
):
    return await entity_service.create_entity(db, data)


@router.get("", response_model=list[EntityOut])
async def list_entities(
    type: EntityType | None = Query(default=None),
    limit: int = Query(default=100, le=1000),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    _: Principal = Depends(get_principal),
):
    return await entity_service.list_entities(db, entity_type=type, limit=limit, offset=offset)


@router.get("/{entity_id}", response_model=EntityOut)
async def get_entity(
    entity_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: Principal = Depends(get_principal),
):
    return await entity_service.get_entity(db, entity_id)


@router.patch("/{entity_id}", response_model=EntityOut)
async def update_entity(
    entity_id: uuid.UUID,
    data: EntityUpdate,
    db: AsyncSession = Depends(get_db),
    _: Principal = Depends(get_principal),
):
    return await entity_service.update_entity(db, entity_id, data)


@router.delete("/{entity_id}", response_model=EntityOut)
async def delete_entity(
    entity_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: Principal = Depends(get_principal),
):
    return await entity_service.delete_entity(db, entity_id)
