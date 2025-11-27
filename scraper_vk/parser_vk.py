import os
import time

from dateparser import parse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

from scraper_vk.const_vk import (
    AVATAR, DATE_PUBLISH, FIRST_PHOTO, LOW_RATING, NAME, RATING, TEXT_REVIEW,
    USER_AGENT,
)
from scraper_vk.database import SessionLocal
from scraper_vk.models import ReviewVK
from scraper_vk.scraper_utils import (
    clean_date, download_link, get_attribute_safe, load_all_reviews,
    upgrade_photo,
)

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
driver.set_window_size(1920, 1080)
action = ActionChains(driver)

driver.get('https://vk.com/reviews-120145172')
time.sleep(2)

count = 0

reviews = load_all_reviews(driver)
for review in reviews:
    rating = len(review.find_elements(*RATING))
    if not review.find_elements(*TEXT_REVIEW) or rating in LOW_RATING:
        continue
    name = review.find_element(*NAME).text
    original_date = parse(review.find_element(*DATE_PUBLISH).text)
    custom_date = clean_date(original_date)
    avatar_src = get_attribute_safe(review, AVATAR, 'src')
    avatar_filename = download_link(avatar_src) or 'default_profile_image.png'

    photo_srcset = get_attribute_safe(review, FIRST_PHOTO, 'srcset')
    first_photo_filename = None

    if photo_srcset:
        clean_url = upgrade_photo(photo_srcset)
        print(f'Есть первое фото. Ссылка: {clean_url}')
        first_photo_filename = download_link(clean_url)

    text_review = review.find_element(*TEXT_REVIEW).text

    new_review = ReviewVK(
        author_name=name,
        rating=rating,
        date_original=original_date,
        date_custom=custom_date,
        text=text_review,
        avatar_filename=avatar_filename,
        first_photo_filename=first_photo_filename,
    )
    db.add(new_review)
    db.commit()
    count += 1
    print(f'Итерация №{count}. Сохранение успешно!')
