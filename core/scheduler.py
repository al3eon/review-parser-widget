import pytz
from apscheduler.schedulers.background import BackgroundScheduler

from core.utils import logger
from scripts.backup_db import backup_process

scheduler = BackgroundScheduler(timezone=pytz.timezone('Europe/Moscow'))


def start_scheduler():
    """Запускает планировщик задач."""
    scheduler.add_job(
        backup_process,
        'cron',
        hour=3,
        minute=0,
        misfire_grace_time=3600,
        id="daily_db_backup",
        replace_existing=True
    )

    scheduler.start()
    logger.info('Планировщик запущен. Резервная копия создастся в 03:00.')
