from app.database import Base, SessionLocal, engine
from core.config import logger
from scraper.vk import VkScraper
from scraper.yandex import YandexScraper


def run_all_parser():
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
    run_all_parser()
