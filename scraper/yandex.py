import time

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from app.models import Review
from core.config import YA_TARGET_URL, logger
from scraper.base import BaseScraper
from scraper.constants import (
    LOW_RATING, YA_AVATAR_LINK, YA_DATE_PUBLISH, YA_DIV_ALL_REVIEWS, YA_NAME,
    YA_RATING, YA_REVIEW_TEXT, YA_SORT_BY_NEW, YA_SORT_STATUS,
    YA_SPOILER_TEXT_BUTTON,
)
from scraper.parsing_utils import download_link, ya_clean_date, ya_clean_url


class YandexScraper(BaseScraper):
    """Реализация скрапера для Яндекс.Карт."""
    def __init__(self, db):
        super().__init__(db)
        self.source_name = 'yandex'

    def _setup_page(self):
        """
        Открывает страницу организации и
        переключает сортировку на 'По новизне'.
        """
        logger.info(f'Открываем страницу: {YA_TARGET_URL}')
        self.driver.get(YA_TARGET_URL)
        time.sleep(15)
        try:
            sort_default = self.driver.find_element(*YA_SORT_STATUS)
            self.driver.execute_script('arguments[0].click();', sort_default)
            sort_by_new = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(YA_SORT_BY_NEW)
            )
            time.sleep(2)
            sort_by_new.click()
            logger.info('Сортировка "По новизне" выбрана успешно')
            time.sleep(2)

        except Exception as e:
            logger.critical(f"Ошибка сортировки! Дальше идти нет смысла. {e}")

    def _load_all_review(self):
        """Динамически подгружает отзывы, скролля контейнер."""
        try:
            action = ActionChains(self.driver)
            prev_count = 0
            while True:
                reviews_elements = self.driver.find_elements(
                    *YA_DIV_ALL_REVIEWS)
                current_count = len(reviews_elements)

                if current_count == prev_count:
                    break

                prev_count = current_count
                action.scroll_to_element(reviews_elements[-1]).perform()
                time.sleep(5)
                logger.info(f'Загружено отзывов: {prev_count}')

            return reviews_elements
        except Exception as e:
            logger.critical(f'Ошибка скрола страницы! {e}')

    def _process_review(self, review_element):
        """Парсит карточку отзыва Яндекса."""
        try:
            rating_char = (review_element.find_element(
                *YA_RATING).get_attribute('aria-label')[7])
            if rating_char in LOW_RATING:
                logger.info('Рейтинг меньше 4. Пропускаем')
                return 'skip'

            author_val = review_element.find_element(*YA_NAME).text
            rating_val = int(rating_char)
            date_val = review_element.find_element(
                *YA_DATE_PUBLISH).get_attribute('content')
            original_date, custom_date = ya_clean_date(date_val)

            existing_review = self.db.query(Review).filter(
                Review.source == self.source_name,
                Review.author_name == author_val,
                Review.date_original == original_date,
            ).first()
            if existing_review:
                logger.info(f'Дубликат: {author_val}')
                return 'duplicate'

            spoilers = review_element.find_elements(*YA_SPOILER_TEXT_BUTTON)
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

            text_val = review_element.find_element(*YA_REVIEW_TEXT).text
            avatar_filename = 'default_profile_image.png'
            try:
                avatar_element = review_element.find_element(*YA_AVATAR_LINK)
                bg_image_raw = avatar_element.value_of_css_property(
                    'background-image'
                )
                avatar_filename = (download_link(
                    ya_clean_url(bg_image_raw)) or 'default_profile_image.png'
                )
                time.sleep(0.5)
            except Exception:
                logger.info(f'У {author_val} аватар не найден. '
                            f'Используем дефолтный.')

            review_data = {
                'author_name': author_val,
                'rating': rating_val,
                'date_original': original_date,
                'date_custom': custom_date,
                'text': text_val,
                'avatar_filename': avatar_filename,
            }

            return self.save_review(review_data)

        except Exception as e:
            logger.error(f'Ошибка парсинга отзыва: {e}')
            return 'skip'
