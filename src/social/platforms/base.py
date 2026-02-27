from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from social.core.enums import Platform


@dataclass
class PostResult:
    platform_post_id: str
    platform_post_url: str | None = None
    raw_response: dict | None = None


@dataclass
class Engagement:
    likes: int = 0
    reposts: int = 0
    replies: int = 0
    views: int = 0
    extra: dict = field(default_factory=dict)


class PlatformAdapter(ABC):
    platform: Platform

    @abstractmethod
    async def publish(self, content: str, media_urls: list[str] | None = None, **kwargs) -> PostResult: ...

    @abstractmethod
    async def delete(self, platform_post_id: str) -> bool: ...

    @abstractmethod
    async def get_engagement(self, platform_post_id: str) -> Engagement: ...

    @abstractmethod
    async def verify_credentials(self, credentials: dict) -> bool: ...
