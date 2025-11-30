import os
from abc import ABC

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth

from app.models import Review
from core.config import logger
from scraper.constants import USER_AGENT

load_dotenv()


class BaseScraper(ABC):
    """Абстрактный базовый класс для всех скраперов."""
    def __init__(self, db_session):
        """Инициализация скрапера."""
        self.db = db_session
        self.driver = None
        self.source_name = 'unknown'

    def init_driver(self):
        """Настраивает и запускает Selenium WebDriver."""
        options = Options()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument(f'--user-agent={USER_AGENT}')
        proxy_url = os.getenv('PROXY_URL')
        if proxy_url:
            clean_proxy = (proxy_url.replace('http://', '')
                           .replace('https://', ''))
            options.add_argument(f'--proxy-server={clean_proxy}')
            logger.info(f'Используется прокси: {clean_proxy}')
        selenium_url = os.getenv('SELENIUM_URL')

        if selenium_url:
            self.driver = webdriver.Remote(
                command_executor=selenium_url,
                options=options
            )
        else:
            self.driver = webdriver.Chrome(options=options)
            stealth(self.driver,
                    languages=['ru-RU', 'ru'],
                    vendor='Google Inc.',
                    platform='Win32',
                    webgl_vendor='Intel Inc.',
                    renderer='Intel Iris OpenGL Engine',
                    fix_hairline=True,
                    )

        self.driver.set_window_size(1920, 1080)

    def quit_driver(self):
        """Безопасно завершает работу драйвера и закрывает браузер."""
        if self.driver:
            self.driver.quit()

    def save_review(self, data: str):
        """Сохраняет отзыв в базу данных."""
        try:
            new_review = Review(
                source=self.source_name,
                author_name=data['author_name'],
                rating=data['rating'],
                date_original=data['date_original'],
                date_custom=data['date_custom'],
                text=data['text'],
                avatar_filename=data['avatar_filename'],
            )
            self.db.add(new_review)
            self.db.commit()
            return 'added'

        except Exception as e:
            logger.error(f'Ошибка БД: {e}')
            self.db.rollback()
            return 'skip'

    def get_attribute_safe(self, element, locator, attribute, default=None):
        """Безопасно получает значение атрибута элемента."""
        found = element.find_elements(*locator)
        if found:
            return found[0].get_attribute(attribute)
        return default

    def run(self):
        """Основной метод запуска."""
        self.init_driver()
        try:
            self._setup_page()
            reviews = self._load_all_review()
            duplicate = 0
            logger.info('Запуск цикла по отзывам...')

            for i, reviews in enumerate(reviews):
                logger.info(f'Итерация №{i + 1}')
                status = self._process_review(reviews)

                if status == 'duplicate':
                    duplicate += 1
                    if duplicate == 3:
                        logger.info('Три дубликата подряд. Стоп.')
                        break
                elif status == 'added':
                    duplicate = 0

        except Exception as e:
            logger.critical(f'Критическая ошибка {self.source_name}: {e}')

        finally:
            self.quit_driver()
