import logging
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / 'data'
LOGS_DIR = DATA_DIR / 'logs'
DB_PATH = DATA_DIR / 'db' / 'reviews.db'

STATIC_DIR = BASE_DIR / 'app' / 'static'
AVATARS_DIR = STATIC_DIR / 'avatars'

LOGS_DIR.mkdir(parents=True, exist_ok=True)
AVATARS_DIR.mkdir(parents=True, exist_ok=True)
(DATA_DIR / 'db').mkdir(parents=True, exist_ok=True)

LOG_FILE = LOGS_DIR / 'scraper.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

YA_TARGET_URL = (os.getenv('YA_TARGET'))
VK_TARGET_URL = (os.getenv('VK_TARGET'))
