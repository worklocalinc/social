import logging
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from social.config import get_settings
from social.core.encryption import decrypt_credentials
from social.core.enums import PostStatus
from social.db.models import Account, Post
from social.platforms.registry import get_adapter

logger = logging.getLogger(__name__)


async def claim_ready_posts(db: AsyncSession, batch_size: int) -> list[Post]:
    now = datetime.now(timezone.utc)
    settings = get_settings()

    stmt = (
        select(Post)
        .where(
            or_(
                Post.status == PostStatus.QUEUED,
                (Post.status == PostStatus.SCHEDULED) & (Post.scheduled_for <= now),
                (Post.status == PostStatus.FAILED)
                & (Post.retry_count < settings.worker_max_retries)
                & (Post.next_retry_at <= now),
            )
        )
        .order_by(Post.created_at)
        .limit(batch_size)
        .with_for_update(skip_locked=True)
    )

    result = await db.execute(stmt)
    posts = list(result.scalars().all())

    if posts:
        post_ids = [p.id for p in posts]
        await db.execute(update(Post).where(Post.id.in_(post_ids)).values(status=PostStatus.POSTING))
        await db.flush()
        for p in posts:
            p.status = PostStatus.POSTING

    return posts


async def process_post(db: AsyncSession, post_id: uuid.UUID) -> None:
    post = await db.get(Post, post_id)
    if not post:
        logger.warning("Post %s not found, skipping", post_id)
        return

    account = await db.get(Account, post.account_id) if post.account_id else None
    if not account or not account.credentials:
        await _fail_post(db, post, "No account or credentials linked to post")
        return

    try:
        credentials = decrypt_credentials(account.credentials)
        adapter = get_adapter(post.platform, credentials)
        result = await adapter.publish(post.content, post.media_urls)

        post.status = PostStatus.POSTED
        post.platform_post_id = result.platform_post_id
        post.platform_post_url = result.platform_post_url
        post.posted_at = datetime.now(timezone.utc)
        post.error = None
        await db.flush()
        logger.info("Posted %s → %s", post.id, result.platform_post_url)

    except Exception as e:
        logger.error("Failed to publish post %s: %s", post.id, e)
        await _fail_post(db, post, str(e))


async def _fail_post(db: AsyncSession, post: Post, error: str) -> None:
    settings = get_settings()
    post.retry_count += 1
    post.error = error

    if post.retry_count < settings.worker_max_retries:
        delay = settings.worker_retry_base_delay * (2 ** (post.retry_count - 1))
        post.next_retry_at = datetime.now(timezone.utc) + timedelta(seconds=delay)
        post.status = PostStatus.FAILED
        logger.info("Post %s retry %d scheduled in %.0fs", post.id, post.retry_count, delay)
    else:
        post.status = PostStatus.FAILED
        post.next_retry_at = None
        logger.warning("Post %s permanently failed after %d retries", post.id, post.retry_count)

    await db.flush()
