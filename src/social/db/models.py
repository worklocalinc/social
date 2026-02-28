import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from social.core.enums import AccountStatus, EntityType, Platform, PostStatus
from social.db.base import Base, SoftDeleteMixin, TimestampMixin, new_uuid


class Entity(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "entities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    type: Mapped[EntityType] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True, default=None)

    accounts: Mapped[list["Account"]] = relationship(back_populates="entity", lazy="selectin")


class Account(Base, TimestampMixin):
    __tablename__ = "accounts"
    __table_args__ = (Index("ix_accounts_entity_platform", "entity_id", "platform"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("entities.id"), nullable=False)
    platform: Mapped[Platform] = mapped_column(String(50), nullable=False)
    platform_user_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    handle: Mapped[str | None] = mapped_column(String(255), nullable=True)
    credentials: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=None)
    status: Mapped[AccountStatus] = mapped_column(String(50), nullable=False, default=AccountStatus.ACTIVE)
    rate_limit_remaining: Mapped[int | None] = mapped_column(nullable=True)
    rate_limit_reset: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True, default=None)

    entity: Mapped["Entity"] = relationship(back_populates="accounts")
    posts: Mapped[list["Post"]] = relationship(back_populates="account", lazy="selectin")


class Post(Base, TimestampMixin):
    __tablename__ = "posts"
    __table_args__ = (
        Index("ix_posts_entity_status", "entity_id", "status"),
        Index("ix_posts_account_status", "account_id", "status"),
        Index("ix_posts_status_scheduled", "status", "scheduled_for"),
        Index(
            "ix_posts_failed_retry",
            "status",
            "next_retry_at",
            postgresql_where=text("status = 'failed'"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("entities.id"), nullable=False)
    account_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True)
    platform: Mapped[Platform] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    media_urls: Mapped[list | None] = mapped_column(JSONB, nullable=True, default=None)
    platform_post_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    platform_post_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    status: Mapped[PostStatus] = mapped_column(String(50), nullable=False, default=PostStatus.QUEUED)
    scheduled_for: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    engagement: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=None)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    retry_count: Mapped[int] = mapped_column(nullable=False, default=0)
    next_retry_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    account: Mapped["Account | None"] = relationship(back_populates="posts")
