from social.core.enums import Platform
from social.platforms.bluesky import BlueskyAdapter
from social.platforms.registry import register_adapter
from social.platforms.twitter import TwitterAdapter

register_adapter(Platform.TWITTER, TwitterAdapter)
register_adapter(Platform.BLUESKY, BlueskyAdapter)
