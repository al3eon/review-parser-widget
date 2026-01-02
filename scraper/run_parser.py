from random import randint

from apscheduler.schedulers.blocking import BlockingScheduler

from app.database import Base, SessionLocal, engine
from core.utils import log_and_alert, logger
from scraper.constants import MAX_MINUTE, MIN_MINUTE
from scraper.vk import VkScraper
from scraper.yandex import YandexScraper
from scripts.backup_db import backup_process


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
                log_and_alert(e, f'Ошибка в {source}')

    except Exception as global_e:
        log_and_alert(global_e, 'Критическая ошибка парсинга')

    finally:
        db.close()
        logger.info('---- Конец общего цикла парсинга ----')


def run_backup():
    """Запуск резервирования БД."""
    logger.info('Запуск резервирования БД')
    try:
        backup_process()
        logger.info('Резервирование завершено успешно')
    except Exception as e:
        log_and_alert(e, 'Ошибка резервирования БД')


def run_parser_then_backup():
    """Парсинг → Бэкап."""
    run_all_parser()
    run_backup()


def get_random_minute():
    """Возвращает случайную минуту от 5 до 55 для планировщика."""
    return randint(MIN_MINUTE, MAX_MINUTE)


if __name__ == '__main__':
    scheduler = BlockingScheduler(timezone='Europe/Moscow')
    random_minute = get_random_minute()
    scheduler.add_job(
        run_parser_then_backup, 'cron', hour=3, minute=random_minute
    )
    logger.info(f'Планировщик парсера и резервного копирования БД запущен. '
                f'Жду 03:{random_minute}...')
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info('Планировщик остановлен.')
