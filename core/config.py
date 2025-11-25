import logging
from pathlib import Path

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

TARGET_URL = ('https://yandex.ru/maps/?ll=38.830636%2C48.471223&mode=poi&poi'
              '%5Bpoint%5D=38.830193%2C48.471345&poi%5Buri%5D=ymapsbm1%3A%2F%2'
              'Forg%3Foid%3D175874439005&tab=reviews&z=18.8')
