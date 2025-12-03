import logging

from aiogram import Bot
from aiogram.types import FSInputFile

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

bot = Bot(token=TG_BOT_TOKEN) if TG_BOT_TOKEN else None


async def send_telegram_message(text: str):
    """Отправляет сообщение в Telegram."""
    if not bot or not TG_CHAT_ID:
        return
    try:
        msg = text[:4000] + '...' if len(text) > 4000 else text
        await bot.send_message(chat_id=TG_CHAT_ID, text=msg)
    except Exception as e:
        logger.error(f'Ошибка при отправке сообщения: {e}')


async def send_telegram_file(file_path: str, caption: str = None):
    """Отправляет файл в Telegram."""
    if not bot or not TG_CHAT_ID:
        return
    try:
        doc = FSInputFile(path=file_path)
        await bot.send_document(chat_id=TG_CHAT_ID,
                                document=doc, caption=caption)
    except Exception as e:
        logger.error(f'Ошибка при отправке файла: {e}')
