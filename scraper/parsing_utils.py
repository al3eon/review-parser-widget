import re
import uuid
from datetime import datetime

import requests

from core.config import AVATARS_DIR, logger
from scraper.constants import USER_AGENT, YA_CUSTOM_MONTH


def ya_clean_date(date_str):
    """
    Преобразует ISO-строку даты Яндекса в объект datetime и
    читаемую строку.
    """
    date_obj = datetime.fromisoformat(date_str.replace('Z', ''))
    display_date = (f'{date_obj.day:02d} '
                    f'{YA_CUSTOM_MONTH[date_obj.month]} {date_obj.year}')

    return date_obj, display_date


def vk_clean_date(date):
    """Форматирует datetime объект в строку формата 'DD month YYYY'."""
    return (f'{date.day:02d} '
            f'{YA_CUSTOM_MONTH[date.month]} {date.year}')


def ya_clean_url(bg_image_raw):
    """Очищает CSS-свойство background-image (url("..."))."""
    clean_url = bg_image_raw.replace('url("', '').replace('")', '')
    final_url = clean_url.replace('islands-68', 'islands-200')
    return final_url


def download_link(url_link):
    """Скачивает изображение по URL, сохраняет в папку AVATARS_DIR"""
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


def vk_improve_quality(url, target_size=150):
    """
    Парсит URL фото ВК и пытается найти ссылку на версию изображения
    с шириной не меньше target_size (по умолчанию 150px).
    """
    if not url:
        return None

    as_match = re.search(r'as=([^&]+)', url)

    if as_match:
        sizes_str = as_match.group(1).split(',')
        best_size = None
        for size in sizes_str:
            try:
                width = int(size.split('x')[0])
                best_size = size
                if width >= target_size:
                    break
            except ValueError:
                continue

        if best_size:
            new_url = re.sub(r'cs=\d+x\d+', f'cs={best_size}', url)
            return new_url

    return url
