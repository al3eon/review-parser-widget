import os
import uuid
from abc import ABC, abstractmethod

import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth

from app.models import Review
from core.config import AVATARS_DIR, logger
from scraper.constants import USER_AGENT

load_dotenv()


class BaseScraper(ABC):
    def __init__(self, db_session):
        self.db = db_session
        self.driver = None
        self.source_name = 'unknown'

    def init_driver(self):
        options = Options()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument(f'--user-agent={USER_AGENT}')
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
        if self.driver:
            self.driver.quit()

    def download_image(self, url_link):
        if url_link:
            try:
                filename = f'{uuid.uuid4()}.jpg'
                file_path = AVATARS_DIR / filename
                headers = {'User-Agent': USER_AGENT}
                response = requests.get(url_link, headers=headers, timeout=10)

                if response.status_code == 200:
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    return filename

            except Exception as e:
                logger.error(f'Ошибка скачивания картинки: {e}')

        return None

    def save_review(self, data: str):
        try:
            new_review = Review(
                source=self.source_name,
                author_name=data['author_name'],
                rating=data['rating'],
                date_original=data['date_original'],
                date_custom=data['date_custom'],
                text=data['text'],
                avatar_filename=data['avatar_filename'],
                photo_url=data.get('photo_url')  # Может быть None
            )
            self.db.add(new_review)
            self.db.commit()
            return 'added'

        except Exception as e:
            logger.error(f'Ошибка БД: {e}')
            self.db.rollback()
            return 'skip'

    def get_attribute_safe(self, element, locator, attribute, default=None):
        found = element.find_elements(*locator)
        if found:
            return found[0].get_attribute(attribute)
        return default

    @abstractmethod
    def run(self):
        """Главный метод запуска."""
