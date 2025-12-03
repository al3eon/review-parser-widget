from random import randint

from apscheduler.schedulers.blocking import BlockingScheduler

from app.database import Base, SessionLocal, engine
from core.utils import log_and_alert_sync, logger
from scraper.constants import MIN_MINUTE, MAX_MINUTE
from scraper.vk import VkScraper
from scraper.yandex import YandexScraper


def run_all_parser():
    """Функция одного прогона всех парсеров"""
    logger.info('---- Начало общего цикла парсинга ---')
    Base.metadata.create_all(engine)
    db = SessionLocal()

    try:
        scrapers = [
            YandexScraper(db),
            VkScraper(db),
        ]
        for scraper in scrapers:
            source = scraper.source_name
            logger.info(f'Запуск модуля {source}')

            try:
                scraper.run()
                logger.info(f'Модуль {source} успешно завершил работу')
            except Exception as e:
                logger.error(f'Ошибка в модуле: {source}: {e}')

    except Exception as global_e:
        log_and_alert_sync(global_e)

    finally:
        db.close()
        logger.info('---- Конец общего цикла парсинга ----')

def get_random_minute():
    """Возвращает случайную минуту от 5 до 55 для планировщика."""
    return randint(MIN_MINUTE, MAX_MINUTE)


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    random_minute = get_random_minute()
    scheduler.add_job(run_all_parser, 'cron', hour=3, minute=random_minute)
    logger.info(f'Планировщик парсера запущен. Жду 03:{random_minute}...')
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info('Планировщик остановлен.')
