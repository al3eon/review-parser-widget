from apscheduler.schedulers.blocking import BlockingScheduler

from app.database import Base, SessionLocal, engine
from core.logger import logger
# from scraper.vk import VkScraper
# from scraper.yandex import YandexScraper


def run_all_parser():
    """Функция одного прогона всех парсеров"""
    logger.info('---- Начало общего цикла парсинга ---')
    Base.metadata.create_all(engine)
    db = SessionLocal()

    try:
        scrapers = [
            # YandexScraper(db),
            # VkScraper(db),
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
        logger.critical(f'Глобальная ошибка при инициализации: {global_e}')

    finally:
        db.close()
        logger.info('---- Конец общего цикла парсинга ----')


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(run_all_parser, 'cron', hour=3, minute=5)
    logger.info('Планировщик парсера запущен. Жду 03:05...')
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info('Планировщик остановлен.')
