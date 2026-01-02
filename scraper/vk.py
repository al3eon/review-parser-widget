import os
import time

from dateparser import parse
from dotenv import load_dotenv
from selenium.common import NoSuchElementException

from app.models import Review
from core.config import VK_TARGET_URL
from core.utils import log_and_alert, logger
from scraper.base import BaseScraper
from scraper.constants import (
    LOW_RATING, VK_AVATAR_LINK, VK_DATE_PUBLISH, VK_DIV_ALL_REVIEWS,
    VK_FIELD_NUMBER, VK_FIELD_PASSWORD, VK_LAST_ELEMENTS, VK_LOGIN,
    VK_LOOK_ALL_REVIEW, VK_MAX_ATTEMPTS, VK_NAME, VK_NUMBER_CONTINUE,
    VK_PASSWORD_CONTINUE, VK_RATING, VK_TEXT_REVIEW,
)
from scraper.parsing_utils import (
    download_link, vk_clean_date, vk_improve_quality,
)

load_dotenv()


class VkScraper(BaseScraper):
    """Реализация скрапера для ВКонтакте."""

    def __init__(self, db):
        super().__init__(db)
        self.source_name = 'vk'

    def check_review_exists(self, author_name, text):
        """Проверяет наличие отзыва по Автору и началу Текста."""
        text_snippet = text[:100]

        exists = self.db.query(Review.id).filter(
            Review.source == self.source_name,
            Review.author_name == author_name,
            Review.text.startswith(text_snippet)
        ).first()
        return exists is not None

    def _setup_page(self):
        """Выполняет вход в ВК и переходит на страницу обсуждений."""
        if os.getenv('VK_LOGIN') and os.getenv('VK_PASSWORD'):
            try:
                self.driver.get('https://vk.com/')
                time.sleep(3)

                self.driver.find_element(*VK_LOGIN).click()
                time.sleep(3)
                field_log = self.driver.find_element(*VK_FIELD_NUMBER)
                field_log.clear()
                field_log.send_keys(os.getenv('VK_LOGIN'))
                time.sleep(2)
                self.driver.find_element(*VK_NUMBER_CONTINUE).click()
                time.sleep(4)

                pass_field = self.driver.find_element(*VK_FIELD_PASSWORD)
                pass_field.click()
                pass_field.send_keys(os.getenv('VK_PASSWORD'))
                time.sleep(3)
                self.driver.find_element(*VK_PASSWORD_CONTINUE).click()
                time.sleep(10)

            except Exception as e:
                log_and_alert(e, f'{self.source_name} авторизация')

        logger.info(f'Открываем страницу: {VK_TARGET_URL}')
        self.driver.get(VK_TARGET_URL)
        time.sleep(10)

    def _load_all_review(self):
        """Скроллит страницу вниз до появления маркера конца списка."""
        max_attempts = VK_MAX_ATTEMPTS
        attempts = 0

        while attempts < max_attempts:
            self.driver.execute_script('window.scrollTo(0, '
                                       'document.body.scrollHeight);')
            time.sleep(3)
            try:
                end_marker = self.driver.find_element(*VK_LOOK_ALL_REVIEW)
                if end_marker.is_displayed():
                    logger.info('Нашли маркер конца списка. '
                                'Загрузка завершена.')
                    break
            except NoSuchElementException:
                pass

            all_reviews = self.driver.find_elements(*VK_DIV_ALL_REVIEWS)
            check_slice = all_reviews[VK_LAST_ELEMENTS:]
            consecutive_duplicates = 0
            for rev in check_slice:
                author = rev.find_element(*VK_NAME).text
                text_elements = rev.find_elements(*VK_TEXT_REVIEW)
                if not text_elements:
                    continue

                text_content = text_elements[0].text
                if self.check_review_exists(author, text_content):
                    consecutive_duplicates += 1
                else:
                    consecutive_duplicates = 0

            if consecutive_duplicates >= 3:
                logger.info('Найдено 3 дубликата подряд. Стоп ВК.')
                break

            self.driver.execute_script('window.scrollBy(0, -1000);')
            time.sleep(4)
            attempts += 1
        else:
            logger.error('Внимание: Достигнут лимит попыток скролла!')
        return self.driver.find_elements(*VK_DIV_ALL_REVIEWS)

    def _process_review(self, review_element):
        """Парсит карточку отзыва ВКонтакте."""
        try:
            rating_val = len(review_element.find_elements(*VK_RATING))
            if not review_element.find_elements(
                    *VK_TEXT_REVIEW) or str(rating_val) in LOW_RATING:
                logger.info('Рейтинг меньше 4. Пропускаем')
                return 'skip'
            author_val = review_element.find_element(*VK_NAME).text
            original_date = parse(review_element.find_element(
                *VK_DATE_PUBLISH).text)
            custom_date = vk_clean_date(original_date)

            existing_review = self.db.query(Review).filter(
                Review.source == self.source_name,
                Review.author_name == author_val,
                Review.date_original == original_date,
            ).first()
            if existing_review:
                logger.info(f'Дубликат: {author_val}')
                return 'duplicate'

            avatar_src = self.get_attribute_safe(
                review_element, VK_AVATAR_LINK, 'src')
            avatar_filename = download_link(
                vk_improve_quality(avatar_src)) or 'default_profile_image.png'

            text_val = review_element.find_element(*VK_TEXT_REVIEW).text

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
            log_and_alert(e, f'{self.source_name} _process_review')
        return 'skip'
