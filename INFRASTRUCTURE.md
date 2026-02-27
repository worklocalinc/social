# Social Service Infrastructure

## Overview
API-first social posting microservice for AI agent fleet.

## Development
- **Local**: http://localhost:8005
- **Postgres**: localhost:5440 (Docker, social/social/social)
- **Redis**: localhost:6387 (Docker)

## Production
- **Status**: Not yet deployed (Phase 1 — scaffold)
- **Target**: TBD (likely Railway or dev server)

## Docker
- `docker-compose.yml`: Postgres 16 + Redis 7 (dev deps)
- `Dockerfile`: Multi-stage python:3.13-slim (for prod deployment)

## Dependencies
- Bots platform (mac-mini-bots @ 192.168.86.50): Agent entities
- Connector service: Shares JWT auth pattern
- Vault (mac-mini-vault @ 192.168.86.27): API keys for social platforms
