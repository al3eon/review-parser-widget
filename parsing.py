import os
import time
import uuid
from datetime import datetime

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

from constants import (
    CUSTOM_MONTH, DATE_VAR, DIV_ALL_REVIEWS,
    LINK, LOW_RATING, NAME,
    RATING, REVIEW_TEXT, USER_AGENT,
)
from database import SessionLocal
from models import Review

if not os.path.exists('downloads'):
    os.makedirs('downloads')

db = SessionLocal()

options = Options()
options.add_argument('--window-size=1920x1080')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument(f'--user-agent={USER_AGENT}')

prefs = {
    'download.default_directory': f'{os.getcwd()}/downloads',
}
options.add_experimental_option('prefs', prefs)
driver = webdriver.Chrome(options=options)
action = ActionChains(driver)


def clean_url(bg_image_raw):
    clean_url = bg_image_raw.replace('url("', '').replace('")', '')
    final_url = clean_url.replace('islands-68', 'islands-200')
    return final_url


def clean_date(date_str):
    date_obj = datetime.fromisoformat(date_str.replace('Z', ''))
    display_date = (f'{date_obj.day:02d} '
                    f'{CUSTOM_MONTH[date_obj.month]} {date_obj.year}')

    return date_obj, display_date


def download_link(url_link):
    if not url_link:
        return None

    try:
        filename = f"{uuid.uuid4()}.jpg"

        headers = {'User-Agent': USER_AGENT}
        response = requests.get(url_link, headers=headers, timeout=10)

        if response.status_code == 200:
            with open(f'downloads/{filename}', 'wb') as f:
                f.write(response.content)
            return filename

    except Exception as e:
        print(f'Ошибка скачивания картинки: {e}')

    return None


file_path = os.path.abspath('test.html')
driver.get(f'file:///{file_path}')
time.sleep(2)

reviews = driver.find_elements(*DIV_ALL_REVIEWS)
print(len(driver.find_elements(*DIV_ALL_REVIEWS)))
print('------------------------------------------------')
count = 0

for review in reviews:
    rating_char = review.find_element(*RATING).get_attribute('aria-label')[7]
    if rating_char in LOW_RATING:
        continue
    name_val = review.find_element(*NAME).text
    rating_val = int(rating_char)
    date_val = review.find_element(*DATE_VAR).get_attribute('content')
    original_date, custom_date = clean_date(date_val)
    review_text_val = review.find_element(*REVIEW_TEXT).text

    try:
        avatar_element = review.find_element(*LINK)
        bg_image_raw = avatar_element.value_of_css_property('background-image')
        bg_image = clean_url(bg_image_raw)

        img_filename = download_link(bg_image)
        time.sleep(0.5)
    except Exception as e:
        print('Аватар не найден: ', e)
        img_filename = None

    new_review = Review(
        author_name=name_val,
        rating=rating_val,
        date_original=original_date,
        date_custom=custom_date,
        text=review_text_val,
        avatar_filename=img_filename,
    )

    db.add(new_review)

    count += 1
    print(f"[{count}] Добавлен в очередь: {name_val} | {custom_date}")

db.commit()
print('Успешно сохранено в базу данных!')