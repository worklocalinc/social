import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from social.api.deps import Principal, get_principal
from social.core.enums import Platform, PostStatus
from social.db.deps import get_db
from social.schemas.posts import PostCreate, PostOut
from social.services import post_service

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("", response_model=PostOut, status_code=201)
async def create_post(
    data: PostCreate,
    db: AsyncSession = Depends(get_db),
    _: Principal = Depends(get_principal),
):
    return await post_service.create_post(db, data)


@router.get("", response_model=list[PostOut])
async def list_posts(
    entity_id: uuid.UUID | None = Query(default=None),
    account_id: uuid.UUID | None = Query(default=None),
    platform: Platform | None = Query(default=None),
    status: PostStatus | None = Query(default=None),
    limit: int = Query(default=100, le=1000),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    _: Principal = Depends(get_principal),
):
    return await post_service.list_posts(
        db, entity_id=entity_id, account_id=account_id, platform=platform, status=status, limit=limit, offset=offset
    )


@router.get("/{post_id}", response_model=PostOut)
async def get_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: Principal = Depends(get_principal),
):
    return await post_service.get_post(db, post_id)


@router.delete("/{post_id}", response_model=PostOut)
async def cancel_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: Principal = Depends(get_principal),
):
    return await post_service.cancel_post(db, post_id)
