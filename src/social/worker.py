import asyncio
import logging
import signal
import sys

# Ensure adapter registration runs
import social.platforms  # noqa: F401
from social.config import get_settings
from social.db.session import async_session
from social.services.publish_service import claim_ready_posts, process_post

logger = logging.getLogger("social.worker")


async def run_worker() -> None:
    settings = get_settings()
    shutdown = asyncio.Event()
    sem = asyncio.Semaphore(settings.worker_concurrency)

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, shutdown.set)

    logger.info(
        "Worker started — poll=%.1fs batch=%d concurrency=%d retries=%d",
        settings.worker_poll_interval,
        settings.worker_batch_size,
        settings.worker_concurrency,
        settings.worker_max_retries,
    )

    while not shutdown.is_set():
        try:
            async with async_session() as db:
                posts = await claim_ready_posts(db, settings.worker_batch_size)
                if posts:
                    logger.info("Claimed %d posts", len(posts))
                    await db.commit()

            async def _process(post_id):
                async with sem:
                    async with async_session() as db:
                        try:
                            await process_post(db, post_id)
                            await db.commit()
                        except Exception:
                            await db.rollback()
                            logger.exception("Unhandled error processing post %s", post_id)

            if posts:
                tasks = [asyncio.create_task(_process(p.id)) for p in posts]
                await asyncio.gather(*tasks)

        except Exception:
            logger.exception("Worker loop error")

        try:
            await asyncio.wait_for(shutdown.wait(), timeout=settings.worker_poll_interval)
        except asyncio.TimeoutError:
            pass

    logger.info("Worker shutting down")


def main() -> None:
    logging.basicConfig(
        level=get_settings().log_level,
        format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    )
    try:
        asyncio.run(run_worker())
    except KeyboardInterrupt:
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
