"""Local-development-only scheduler for repeatedly running the StormWatch ETL.

Do not use this module in AWS, ECS, or any other production environment.
Production scheduling is handled by EventBridge Scheduler, which launches the
one-shot ``scripts/run_pipeline.py`` entry point from ``Dockerfile.worker``.
"""

import logging
import os
import signal
import subprocess
import sys
from threading import Event

logger = logging.getLogger("stormwatch.worker")
stop_requested = Event()
active_process: subprocess.Popen | None = None

# LOCAL DEVELOPMENT ONLY. Keep this scheduler disabled by default and never
# enable it implicitly through an environment variable or production image.
SCHEDULING_ENABLED = False


def request_stop(signum: int, _frame: object) -> None:
    logger.info("Worker received signal %s; stopping.", signum)
    stop_requested.set()
    if active_process is not None and active_process.poll() is None:
        active_process.terminate()


def run_scheduler() -> None:
    global active_process
    interval = int(os.getenv("PIPELINE_INTERVAL_SECONDS", "3600"))
    if interval < 1:
        raise ValueError("PIPELINE_INTERVAL_SECONDS must be at least 1")

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)

    while not stop_requested.is_set():
        logger.info("Starting scheduled StormWatch pipeline run.")
        active_process = subprocess.Popen(
            [sys.executable, "scripts/run_pipeline.py"],
        )
        return_code = active_process.wait()
        active_process = None
        if return_code:
            logger.error(
                "Pipeline exited with status %s; worker will retry next cycle.",
                return_code,
            )
        else:
            logger.info("Scheduled pipeline run finished.")

        if not stop_requested.is_set():
            logger.info("Next run in %s seconds.", interval)
            stop_requested.wait(interval)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    if not SCHEDULING_ENABLED:
        logger.warning(
            "Local-development-only scheduling is disabled; no pipeline was run."
        )
        return

    run_scheduler()


if __name__ == "__main__":
    main()
