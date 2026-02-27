from social.core.enums import Platform
from social.platforms.base import PlatformAdapter

_adapters: dict[Platform, type[PlatformAdapter]] = {}


def register_adapter(platform: Platform, adapter_cls: type[PlatformAdapter]) -> None:
    _adapters[platform] = adapter_cls


def get_adapter(platform: Platform, credentials: dict) -> PlatformAdapter:
    adapter_cls = _adapters.get(platform)
    if adapter_cls is None:
        raise ValueError(f"No adapter registered for platform: {platform}")
    return adapter_cls(credentials=credentials)


def list_adapters() -> list[Platform]:
    return list(_adapters.keys())
