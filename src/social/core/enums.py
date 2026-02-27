from enum import StrEnum


class Platform(StrEnum):
    TWITTER = "twitter"
    BLUESKY = "bluesky"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    THREADS = "threads"


class EntityType(StrEnum):
    AGENT = "agent"
    PROJECT = "project"
    USER = "user"


class AccountStatus(StrEnum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    ERROR = "error"


class PostStatus(StrEnum):
    QUEUED = "queued"
    SCHEDULED = "scheduled"
    POSTING = "posting"
    POSTED = "posted"
    FAILED = "failed"
