from __future__ import annotations

import logging
from typing import Callable

from apscheduler.schedulers.blocking import BlockingScheduler

from .config import Settings


class BotScheduler:
    def __init__(self, settings: Settings, logger: logging.Logger) -> None:
        self.settings = settings
        self.logger = logger
        self.scheduler = BlockingScheduler(timezone=settings.scheduler_timezone)

    def start(self, job: Callable[[], None]) -> None:
        self.scheduler.add_job(
            job,
            trigger="interval",
            minutes=self.settings.scan_interval_minutes,
            max_instances=1,
            coalesce=True,
        )
        self.logger.info(
            "Scheduler started. Interval=%s minute(s), timezone=%s",
            self.settings.scan_interval_minutes,
            self.settings.scheduler_timezone,
        )
        job()
        self.scheduler.start()
