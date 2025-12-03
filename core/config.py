import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
LOGS_DIR = DATA_DIR / 'logs'
BACKUP_DIR = DATA_DIR / 'backups'
DB_PATH = DATA_DIR / 'db' / 'reviews.db'
STATIC_DIR = BASE_DIR / 'app' / 'static'
AVATARS_DIR = STATIC_DIR / 'avatars'

YA_TARGET_URL = (os.getenv('YA_TARGET'))
VK_TARGET_URL = (os.getenv('VK_TARGET'))
TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')

ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*').split(',')