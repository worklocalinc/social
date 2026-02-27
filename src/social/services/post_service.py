import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from social.core.enums import Platform, PostStatus
from social.core.exceptions import BadRequest, NotFound
from social.db.models import Post
from social.schemas.posts import PostCreate


async def create_post(db: AsyncSession, data: PostCreate) -> Post:
    status = PostStatus.SCHEDULED if data.scheduled_for else PostStatus.QUEUED

    post = Post(
        entity_id=data.entity_id,
        account_id=data.account_id,
        platform=data.platform,
        content=data.content,
        media_urls=data.media_urls,
        status=status,
        scheduled_for=data.scheduled_for,
        source=data.source,
    )
    db.add(post)
    await db.flush()
    await db.refresh(post)
    return post


async def get_post(db: AsyncSession, post_id: uuid.UUID) -> Post:
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise NotFound("Post not found")
    return post


async def list_posts(
    db: AsyncSession,
    entity_id: uuid.UUID | None = None,
    account_id: uuid.UUID | None = None,
    platform: Platform | None = None,
    status: PostStatus | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Post]:
    q = select(Post)
    if entity_id:
        q = q.where(Post.entity_id == entity_id)
    if account_id:
        q = q.where(Post.account_id == account_id)
    if platform:
        q = q.where(Post.platform == platform)
    if status:
        q = q.where(Post.status == status)
    q = q.order_by(Post.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(q)
    return list(result.scalars().all())


async def cancel_post(db: AsyncSession, post_id: uuid.UUID) -> Post:
    post = await get_post(db, post_id)
    if post.status not in (PostStatus.QUEUED, PostStatus.SCHEDULED):
        raise BadRequest(f"Cannot cancel post with status '{post.status}'")
    await db.delete(post)
    await db.flush()
    return post
