FROM python:3.13-slim AS base

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl && \
    rm -rf /var/lib/apt/lists/*

FROM base AS builder
COPY pyproject.toml .
RUN pip install --no-cache-dir .

FROM base AS runtime
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY alembic.ini .
COPY alembic/ alembic/
COPY src/ src/
COPY scripts/entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 8005
ENTRYPOINT ["./entrypoint.sh"]
