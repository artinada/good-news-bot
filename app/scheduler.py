import asyncio

from apscheduler.schedulers.blocking import BlockingScheduler
from main import run

scheduler = BlockingScheduler(
    timezone="Europe/Berlin"
)


def job():
    asyncio.run(run())


scheduler.add_job(
    job,
    "cron",
    hour=7,
    minute=0
)

scheduler.start()
