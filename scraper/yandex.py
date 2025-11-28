import time

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from app.models import Review
from core.config import TARGET_URL, logger
from scraper.base import BaseScraper
from scraper.constants import (
    DATE_VAR, DIV_ALL_REVIEWS, LINK, LOW_RATING, NAME, RATING, REVIEW_TEXT,
    SORT_BY_NEW, SORT_STATUS, SPOILER_TEXT_BUTTON,
)
from scraper.parsing_utils import clean_date, clean_url, download_link


class YandexScraper(BaseScraper):
    def __init__(self, db):
        super().__init__(db)
        self.source_name = "yandex"

    def _setup_page(self):
        logger.info(f'Открываем страницу: {TARGET_URL}')
        self.driver.get(TARGET_URL)
        time.sleep(15)
        try:
            sort_default = self.driver.find_element(*SORT_STATUS)
            self.driver.execute_script('arguments[0].click();', sort_default)
            sort_by_new = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(SORT_BY_NEW)
            )
            time.sleep(2)
            sort_by_new.click()
            logger.info('Сортировка "По новизне" выбрана успешно')
            time.sleep(2)

        except Exception as e:
            logger.critical(f"Ошибка сортировки! Дальше идти нет смысла. {e}")

    def _load_all_review(self):
        try:
            action = ActionChains(self.driver)
            prev_count = 0
            while True:
                reviews_elements = self.driver.find_elements(*DIV_ALL_REVIEWS)
                current_count = len(reviews_elements)

                if current_count == prev_count:
                    break

                prev_count = current_count
                action.scroll_to_element(reviews_elements[5]).perform()
                time.sleep(5)
                logger.info(f'Загружено отзывов: {prev_count}')

            return reviews_elements
        except Exception as e:
            logger.critical(f'Ошибка скрола страницы! {e}')

    def _process_review(self, review_element):
        try:
            rating_char = (review_element.find_element(
                *RATING).get_attribute('aria-label')[7])
            if rating_char in LOW_RATING:
                logger.info('Рейтинг меньше 4. Пропускаем')
                return 'skip'

            name_val = review_element.find_element(*NAME).text
            rating_val = int(rating_char)
            date_val = review_element.find_element(
                *DATE_VAR).get_attribute('content')
            original_date, custom_date = clean_date(date_val)

            existing_review = self.db.query(Review).filter(
                Review.author_name == name_val,
                Review.date_original == original_date,
            ).first()
            if existing_review:
                logger.info(f'Дубликат: {name_val}')
                return 'duplicate'

            spoilers = review_element.find_elements(*SPOILER_TEXT_BUTTON)
            if spoilers:
                element = spoilers[0]
                self.driver.execute_script(
                    'arguments[0].scrollIntoView('
                    '{block: "nearest", inline: "nearest"});',
                    element
                )
                time.sleep(1)
                self.driver.execute_script('arguments[0].click();', element)
                time.sleep(1)

            text_val = review_element.find_element(*REVIEW_TEXT).text
            avatar_filename = 'default_profile_image.png'
            try:
                avatar_element = review_element.find_element(*LINK)
                bg_image_raw = avatar_element.value_of_css_property(
                    'background-image'
                )
                avatar_filename = (download_link(
                    clean_url(bg_image_raw)) or 'default_profile_image.png'
                )
                time.sleep(0.5)
            except Exception:
                logger.info(f'У {name_val} аватар не найден. '
                            f'Используем дефолтный.')

            review_data = {
                'author_name': name_val,
                'rating': rating_val,
                'date_original': original_date,
                'date_custom': custom_date,
                'text': text_val,
                'avatar_filename': avatar_filename,
                'photo_url': None
            }

            return self.save_review(review_data)

        except Exception as e:
            logger.error(f'Ошибка парсинга отзывов: {e}')
            return 'skip'

    def run(self):
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
            logger.critical(f'Критическая ошибка Yandex: {e}')

        finally:
            self.quit_driver()
