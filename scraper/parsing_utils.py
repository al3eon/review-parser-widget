import uuid
from datetime import datetime

import requests

from core.config import AVATARS_DIR, logger
from scraper.constants import CUSTOM_MONTH, USER_AGENT


def clean_date(date_str):
    date_obj = datetime.fromisoformat(date_str.replace('Z', ''))
    display_date = (f'{date_obj.day:02d} '
                    f'{CUSTOM_MONTH[date_obj.month]} {date_obj.year}')

    return date_obj, display_date


def clean_url(bg_image_raw):
    clean_url = bg_image_raw.replace('url("', '').replace('")', '')
    final_url = clean_url.replace('islands-68', 'islands-200')
    return final_url


def download_link(url_link):
    if not url_link:
        return None

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
