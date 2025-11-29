import os
import time

from dateparser import parse
from dotenv import load_dotenv
from selenium.common import NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains

from app.models import Review
from core.config import VK_TARGET_URL, logger
from scraper.base import BaseScraper
from scraper.constants import (
    LOW_RATING, VK_AVATAR_LINK, VK_DATE_PUBLISH, VK_DIV_ALL_REVIEWS,
    VK_FIELD_NUMBER, VK_FIELD_PASSWORD, VK_LOGIN,
    VK_LOOK_ALL_REVIEW, VK_MAX_ATTEMPTS, VK_NAME, VK_NUMBER_CONTINUE,
    VK_PASSWORD_CONTINUE, VK_RATING, VK_TEXT_REVIEW,
)
from scraper.parsing_utils import (
    download_link, vk_clean_date, vk_improve_quality
)

load_dotenv()


class VkScraper(BaseScraper):
    def __init__(self, db):
        super().__init__(db)
        self.source_name = 'vk'

    def _setup_page(self):
        self.driver.get('https://vk.com/')
        time.sleep(5)
        self.driver.find_element(*VK_LOGIN).click()
        time.sleep(3)
        action = ActionChains(self.driver)
        field_log = self.driver.find_element(*VK_FIELD_NUMBER)
        action.send_keys_to_element(
            field_log, Keys.BACKSPACE).send_keys_to_element(
            field_log, Keys.BACKSPACE).pause(2).send_keys(
            os.getenv('VK_LOGIN')).perform()
        time.sleep(4)
        self.driver.find_element(*VK_NUMBER_CONTINUE).click()
        time.sleep(4)
        self.driver.find_element(*VK_FIELD_PASSWORD).click()
        action.send_keys_to_element(self.driver.find_element(
            *VK_FIELD_PASSWORD), os.getenv('VK_PASSWORD')).perform()
        time.sleep(3)
        self.driver.find_element(*VK_PASSWORD_CONTINUE).click()
        time.sleep(10)

        logger.info(f'Открываем страницу: {VK_TARGET_URL}')
        self.driver.get(VK_TARGET_URL)
        time.sleep(10)

    def _load_all_review(self):
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
            self.driver.execute_script('window.scrollBy(0, -1000);')
            time.sleep(4)
            attempts += 1
        else:
            logger.error('Внимание: Достигнут лимит попыток скролла!')
        return self.driver.find_elements(*VK_DIV_ALL_REVIEWS)

    def _process_review(self, review_element):
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
            logger.error(f'Ошибка парсинга отзыва: {e}')
        return 'skip'
