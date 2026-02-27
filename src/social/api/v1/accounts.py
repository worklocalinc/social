import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from social.api.deps import Principal, get_principal
from social.core.enums import Platform
from social.db.deps import get_db
from social.schemas.accounts import AccountCreate, AccountOut, AccountUpdate
from social.services import account_service

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("", response_model=AccountOut, status_code=201)
async def create_account(
    data: AccountCreate,
    db: AsyncSession = Depends(get_db),
    _: Principal = Depends(get_principal),
):
    return await account_service.create_account(db, data)


@router.get("", response_model=list[AccountOut])
async def list_accounts(
    entity_id: uuid.UUID | None = Query(default=None),
    platform: Platform | None = Query(default=None),
    limit: int = Query(default=100, le=1000),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    _: Principal = Depends(get_principal),
):
    return await account_service.list_accounts(db, entity_id=entity_id, platform=platform, limit=limit, offset=offset)


@router.get("/{account_id}", response_model=AccountOut)
async def get_account(
    account_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: Principal = Depends(get_principal),
):
    return await account_service.get_account(db, account_id)


@router.patch("/{account_id}", response_model=AccountOut)
async def update_account(
    account_id: uuid.UUID,
    data: AccountUpdate,
    db: AsyncSession = Depends(get_db),
    _: Principal = Depends(get_principal),
):
    return await account_service.update_account(db, account_id, data)


@router.delete("/{account_id}", status_code=204)
async def delete_account(
    account_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: Principal = Depends(get_principal),
):
    await account_service.delete_account(db, account_id)


@router.post("/{account_id}/verify")
async def verify_account(
    account_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: Principal = Depends(get_principal),
):
    return await account_service.verify_account(db, account_id)
