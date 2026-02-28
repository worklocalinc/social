import logging

import httpx

from social.core.enums import Platform
from social.platforms.base import Engagement, PlatformAdapter, PostResult

logger = logging.getLogger(__name__)

TWITTER_API = "https://api.twitter.com/2"


class TwitterAdapter(PlatformAdapter):
    platform = Platform.TWITTER

    def __init__(self, credentials: dict):
        self.bearer_token = credentials["bearer_token"]
        self._headers = {"Authorization": f"Bearer {self.bearer_token}"}

    async def publish(self, content: str, media_urls: list[str] | None = None, **kwargs) -> PostResult:
        payload: dict = {"text": content}
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{TWITTER_API}/tweets", headers=self._headers, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()["data"]
            tweet_id = data["id"]
            return PostResult(
                platform_post_id=tweet_id,
                platform_post_url=f"https://x.com/i/status/{tweet_id}",
                raw_response=data,
            )

    async def delete(self, platform_post_id: str) -> bool:
        async with httpx.AsyncClient() as client:
            resp = await client.delete(f"{TWITTER_API}/tweets/{platform_post_id}", headers=self._headers, timeout=30)
            resp.raise_for_status()
            return resp.json().get("data", {}).get("deleted", False)

    async def get_engagement(self, platform_post_id: str) -> Engagement:
        params = {"tweet.fields": "public_metrics"}
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{TWITTER_API}/tweets/{platform_post_id}", headers=self._headers, params=params, timeout=30
            )
            resp.raise_for_status()
            metrics = resp.json().get("data", {}).get("public_metrics", {})
            return Engagement(
                likes=metrics.get("like_count", 0),
                reposts=metrics.get("retweet_count", 0),
                replies=metrics.get("reply_count", 0),
                views=metrics.get("impression_count", 0),
                extra={"quote_count": metrics.get("quote_count", 0)},
            )

    async def verify_credentials(self, credentials: dict) -> bool:
        token = credentials.get("bearer_token", self.bearer_token)
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{TWITTER_API}/users/me", headers=headers, timeout=15)
            return resp.status_code == 200
