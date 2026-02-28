import logging

from atproto import AsyncClient

from social.core.enums import Platform
from social.platforms.base import Engagement, PlatformAdapter, PostResult

logger = logging.getLogger(__name__)


class BlueskyAdapter(PlatformAdapter):
    platform = Platform.BLUESKY

    def __init__(self, credentials: dict):
        self.handle = credentials["handle"]
        self.app_password = credentials["app_password"]
        self._client: AsyncClient | None = None

    async def _get_client(self) -> AsyncClient:
        if self._client is None:
            self._client = AsyncClient()
            await self._client.login(self.handle, self.app_password)
        return self._client

    async def publish(self, content: str, media_urls: list[str] | None = None, **kwargs) -> PostResult:
        client = await self._get_client()
        resp = await client.send_post(text=content)
        # resp.uri is like at://did:plc:xxx/app.bsky.feed.post/yyy
        parts = resp.uri.split("/")
        rkey = parts[-1]
        did = parts[2]
        post_url = f"https://bsky.app/profile/{did}/post/{rkey}"
        return PostResult(
            platform_post_id=resp.uri,
            platform_post_url=post_url,
            raw_response={"uri": resp.uri, "cid": resp.cid},
        )

    async def delete(self, platform_post_id: str) -> bool:
        client = await self._get_client()
        await client.delete_post(platform_post_id)
        return True

    async def get_engagement(self, platform_post_id: str) -> Engagement:
        client = await self._get_client()
        thread = await client.get_post_thread(platform_post_id)
        post = thread.thread.post
        return Engagement(
            likes=post.like_count or 0,
            reposts=post.repost_count or 0,
            replies=post.reply_count or 0,
        )

    async def verify_credentials(self, credentials: dict) -> bool:
        try:
            client = AsyncClient()
            await client.login(
                credentials.get("handle", self.handle),
                credentials.get("app_password", self.app_password),
            )
            return True
        except Exception:
            logger.debug("Bluesky credential verification failed", exc_info=True)
            return False
