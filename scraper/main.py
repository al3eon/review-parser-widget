import time

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from app.database import Base, SessionLocal, engine
from app.models import Review
from core.config import TARGET_URL, logger
from scraper.browser import init_driver
from scraper.constants import (
    DATE_VAR, DIV_ALL_REVIEWS, LINK, LOW_RATING, NAME, RATING, REVIEW_TEXT,
    SORT_BY_NEW, SORT_STATUS, SPOILER_TEXT_BUTTON,
)
from scraper.parsing_utils import clean_date, clean_url, download_link


def setup_page(driver):
    try:
        logger.info(f'Открываем страницу: {TARGET_URL}')
        driver.get(TARGET_URL)
        time.sleep(15)
        sort_default = driver.find_element(*SORT_STATUS)
        driver.execute_script('arguments[0].click();', sort_default)
        sort_by_new = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(SORT_BY_NEW)
        )
        time.sleep(2)
        sort_by_new.click()
        logger.info('Сортировка "По новизне" выбрана успешно')

    except Exception as e:
        logger.critical(f"Ошибка сортировки! Дальше идти нет смысла. {e}")


def load_all_reviews(driver, action):
    try:
        prev_count = 0
        while True:
            reviews_elements = driver.find_elements(*DIV_ALL_REVIEWS)
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


def process_single_review(driver, review, db):
    try:
        rating_char = (review.find_element(
            *RATING).get_attribute('aria-label')[7])
        if rating_char in LOW_RATING:
            logger.info('Рейтинг меньше 4. Пропускаем')
            return 'skip'

        name_val = review.find_element(*NAME).text
        rating_val = int(rating_char)
        date_val = review.find_element(*DATE_VAR).get_attribute('content')
        original_date, custom_date = clean_date(date_val)

        existing_review = db.query(Review).filter(
            Review.author_name == name_val,
            Review.date_original == original_date,
        ).first()
        if existing_review:
            logger.info(f'Дубликат: {name_val}')
            return 'duplicate'

        spoilers = review.find_elements(*SPOILER_TEXT_BUTTON)
        if spoilers:
            element = spoilers[0]
            driver.execute_script(
                'arguments[0].scrollIntoView('
                '{block: "nearest", inline: "nearest"});',
                element
            )
            time.sleep(1)
            driver.execute_script('arguments[0].click();', element)
            time.sleep(1)
        review_text_val = review.find_element(*REVIEW_TEXT).text
        img_filename = 'default_profile_image.png'
        try:
            avatar_element = review.find_element(*LINK)
            bg_image_raw = avatar_element.value_of_css_property(
                'background-image'
            )
            img_filename = (download_link(
                clean_url(bg_image_raw)) or 'default_profile_image.png'
            )
            time.sleep(0.5)
        except Exception:
            logger.info(f'У {name_val} аватар не найден. '
                        f'Используем дефолтный.')

        new_review = Review(
            author_name=name_val,
            rating=rating_val,
            date_original=original_date,
            date_custom=custom_date,
            text=review_text_val,
            avatar_filename=img_filename,
        )
        db.add(new_review)
        db.commit()

        return 'added'

    except Exception as e:
        logger.error(f'Ошибка при обработке конкретного отзыва: {e}')
        return 'skip'


def run_parser():
    logger.info('Запуск парсера...')
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    driver = init_driver()
    action = ActionChains(driver)
    try:
        setup_page(driver)
        reviews_elements = load_all_reviews(driver, action)
        duplicate_review = 0

        for i, review in enumerate(reviews_elements):
            logger.info(f'Начинаем {i + 1} итерацию!')
            status = process_single_review(driver, review, db)

            if status == 'duplicate':
                duplicate_review += 1
                if duplicate_review == 3:
                    logger.info('Три дубликата подряд. Остановка цикла')
                    break

            elif status == 'added':
                duplicate_review = 0
                logger.info(f'{i + 1} успешно добавлен')

    except Exception as main_e:
        logger.critical(f"Критическая ошибка всего скрипта: {main_e}")
    finally:
        driver.quit()
        db.close()
        logger.info('Работа завершена.')


if __name__ == '__main__':
    run_parser()
