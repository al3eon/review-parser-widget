import logging
import requests

from core.config import (
    AVATARS_DIR, DATA_DIR, LOGS_DIR, TG_BOT_TOKEN, TG_CHAT_ID,
)

for path in [LOGS_DIR, AVATARS_DIR, DATA_DIR / 'db']:
    path.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOGS_DIR / 'scraper.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('review_service')


def send_telegram_message(text: str):
    """Отправляет сообщение в Telegram (синхронно)."""
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        return
    try:
        msg = text[:4000] + '...' if len(text) > 4000 else text
        requests.post(
            f'https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage',
            json={'chat_id': TG_CHAT_ID, 'text': msg},
            timeout=10
        )
    except Exception as e:
        logger.error(f'Ошибка при отправке сообщения: {e}')


def send_telegram_file(file_path: str, caption: str = None):
    """Отправляет файл в Telegram (синхронно)."""
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        return
    try:
        with open(file_path, 'rb') as f:
            requests.post(
                f'https://api.telegram.org/bot{TG_BOT_TOKEN}/sendDocument',
                data={'chat_id': TG_CHAT_ID, 'caption': caption or ''},
                files={'document': f},
                timeout=10
            )
    except Exception as e:
        logger.error(f'Ошибка при отправке файла: {e}')


def log_and_alert(error, context=''):
    """Логирование и отправка оповещений (синхронно)."""
    text = (f'Ошибка в {context}:\n{error}' if context else
            f'Ошибка:\n{error}')

    if isinstance(error, Exception):
        logger.error(f'{context}: {error}', exc_info=True)
    else:
        logger.error(f'{context}: {error}')

    send_telegram_message(text)
