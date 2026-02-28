import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from social.core.encryption import decrypt_credentials, encrypt_credentials
from social.core.enums import Platform
from social.core.exceptions import NotFound
from social.db.models import Account
from social.platforms.registry import get_adapter
from social.schemas.accounts import AccountCreate, AccountUpdate

logger = logging.getLogger(__name__)


async def create_account(db: AsyncSession, data: AccountCreate) -> Account:
    credentials = encrypt_credentials(data.credentials) if data.credentials else None

    account = Account(
        entity_id=data.entity_id,
        platform=data.platform,
        platform_user_id=data.platform_user_id,
        handle=data.handle,
        credentials=credentials,
        metadata_=data.metadata,
    )
    db.add(account)
    await db.flush()
    await db.refresh(account)
    return account


async def get_account(db: AsyncSession, account_id: uuid.UUID) -> Account:
    result = await db.execute(select(Account).where(Account.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise NotFound("Account not found")
    return account


async def list_accounts(
    db: AsyncSession,
    entity_id: uuid.UUID | None = None,
    platform: Platform | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Account]:
    q = select(Account)
    if entity_id:
        q = q.where(Account.entity_id == entity_id)
    if platform:
        q = q.where(Account.platform == platform)
    q = q.order_by(Account.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(q)
    return list(result.scalars().all())


async def update_account(db: AsyncSession, account_id: uuid.UUID, data: AccountUpdate) -> Account:
    account = await get_account(db, account_id)
    update_data = data.model_dump(exclude_unset=True)

    if "credentials" in update_data and update_data["credentials"] is not None:
        update_data["credentials"] = encrypt_credentials(update_data["credentials"])

    if "metadata" in update_data:
        update_data["metadata_"] = update_data.pop("metadata")

    for field, value in update_data.items():
        setattr(account, field, value)
    await db.flush()
    await db.refresh(account)
    return account


async def delete_account(db: AsyncSession, account_id: uuid.UUID) -> None:
    account = await get_account(db, account_id)
    await db.delete(account)
    await db.flush()


async def verify_account(db: AsyncSession, account_id: uuid.UUID) -> dict:
    account = await get_account(db, account_id)
    if not account.credentials:
        return {"status": "error", "message": "No credentials stored for this account"}
    try:
        credentials = decrypt_credentials(account.credentials)
        adapter = get_adapter(account.platform, credentials)
        valid = await adapter.verify_credentials(credentials)
        if valid:
            return {"status": "ok", "message": f"{account.platform} credentials verified"}
        return {"status": "error", "message": f"{account.platform} credential verification failed"}
    except ValueError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        logger.error("Credential verification error for account %s: %s", account_id, e)
        return {"status": "error", "message": f"Verification failed: {e}"}
