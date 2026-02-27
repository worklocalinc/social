# Social Service

API-first social posting microservice for 600+ AI agents.

## Stack
- Python 3.12+ / FastAPI / SQLAlchemy 2.0 async / Alembic
- Postgres 16 (port 5440) + Redis 7 (port 6387)
- JWT + admin token auth, Fernet credential encryption

## Quick Start
```bash
docker compose up -d     # Start Postgres + Redis
pip install -e ".[dev]"  # Install deps
make migrate             # Run migrations
make run                 # Start on :8005
```

## Patterns
- **Package**: `social` — all imports `from social.xxx`
- **Config**: Flat pydantic-settings with `lru_cache` singleton
- **Auth**: HTTPBearer → Principal dataclass → require_permissions() factory
- **Models**: SQLAlchemy 2.0 mapped_column, UUID PKs, JSONB, TimestampMixin/SoftDeleteMixin
- **Services**: Module-level async functions taking `db: AsyncSession`
- **Routes**: Thin handlers delegating to services
- **Encryption**: Fernet encrypt/decrypt for credential JSONB fields

## API
- Base: `http://localhost:8005`
- Health: `GET /api/v1/health`
- Entities: `/api/v1/entities` (CRUD)
- Accounts: `/api/v1/accounts` (CRUD + verify)
- Posts: `/api/v1/posts` (CRUD)

## Database
- Migrations: `make revision msg="description"` then `make migrate`
- Reset: `make reset`
- Tables: entities, accounts, posts

## Auth
- Admin token: `Authorization: Bearer <ADMIN_TOKEN>`
- JWT: `Authorization: Bearer <jwt>` (from bots/connector)
