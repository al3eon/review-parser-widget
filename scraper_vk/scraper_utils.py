import time
import uuid
from pathlib import Path

import requests
from selenium.common import NoSuchElementException

from scraper.constants import CUSTOM_MONTH, USER_AGENT
from scraper_vk.const_vk import DIV_ALL_REVIE, LOOK_ALL_REVIEW, MAX_ATTEMPTS

BASE_DIR = Path(__file__).resolve().parent
FILE_PATH = BASE_DIR / 'downloads'
FILE_PATH.mkdir(parents=True, exist_ok=True)


def load_all_reviews(driver):
    max_attempts = MAX_ATTEMPTS
    attempts = 0

    while attempts < max_attempts:
        driver.execute_script('window.scrollTo(0, '
                              'document.body.scrollHeight);')
        time.sleep(2)
        try:
            end_marker = driver.find_element(*LOOK_ALL_REVIEW)
            if end_marker.is_displayed():
                print('Нашли маркер конца списка. Загрузка завершена.')
                break
        except NoSuchElementException:
            pass
        driver.execute_script('window.scrollBy(0, -1000);')
        time.sleep(3)
        attempts += 1
    else:
        print('Внимание: Достигнут лимит попыток скролла!')
    return driver.find_elements(*DIV_ALL_REVIE)


def download_link(url_link):
    if not url_link:
        return None

    try:
        filename = f'{uuid.uuid4()}.jpg'
        file_path = FILE_PATH / filename
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(url_link, headers=headers, timeout=10)

        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(response.content)
            return filename

    except Exception as e:
        print(f'Ошибка скачивания картинки: {e}')

    return None


def clean_date(date_obj):
    return (f'{date_obj.day:02d} '
            f'{CUSTOM_MONTH[date_obj.month]} {date_obj.year}')


def upgrade_photo(element):
    best_quality_string = element.split(',')[-1].strip()
    final_url = best_quality_string.split(' ')[0]
    return final_url


def get_attribute_safe(element, locator, attribute, default=None):
    found = element.find_elements(*locator)
    if found:
        return found[0].get_attribute(attribute)
    return default
